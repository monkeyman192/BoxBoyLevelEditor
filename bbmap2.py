import struct
from lxml import etree
from io import BytesIO
from PIL import Image, ImageTk


def read_int32(fobj):
    return struct.unpack('<i', fobj.read(0x4))[0]


def read_tuple16(fobj):
    return struct.unpack('<hh', fobj.read(0x4))


def write_int32(fobj, data):
    fobj.write(struct.pack('<i', data))


def write_tuple16(fobj, data):
    fobj.write(struct.pack('<hh', data[0], data[1]))


def write_int32_array(fobj, data):
    # flip the data
    d = data[::-1]
    for row in d:
        for value in row:
            write_int32(fobj, value)


class BBMap():
    def __init__(self, fpath):
        self.fpath = fpath

        with open(fpath, 'rb') as fobj:
            self._read_header(fobj)
            self._read_map_layout(fobj)
            self._read_moving_platform_data(fobj)
            self._read_movable_blocks(fobj)
            self._read_map_layers(fobj)
            self._read_gimmick_data(fobj)
            # skip whatever the next pointer goes to as it is always empty...
            fobj.seek(0x4, 1)
            self._read_moving_platform_path_data(fobj)

    def export(self):
        """ Export all the data. """
        pass

    def _read_header(self, fobj):
        self.magic = struct.unpack('4s', fobj.read(0x4))[0]
        if not self.magic == b'XBIN':
            raise ValueError('Provided file is not a valid BoxBoy map file')
        self.version = read_int32(fobj)
        self.filesize = read_int32(fobj)
        self.unknown_value0 = read_int32(fobj)
        self.box_number = read_int32(fobj)
        self.box_set_num = read_int32(fobj)
        self.camera_height = read_int32(fobj)
        self.sound_tag = read_int32(fobj)

    def _write_header(self):
        self._bytes.write(struct.pack('4s', self.magic))
        write_int32(self._bytes, self.version)
        write_int32(self._bytes, 0)
        write_int32(self._bytes, self.unknown_value0)
        write_int32(self._bytes, self.box_number)
        write_int32(self._bytes, self.box_set_num)
        write_int32(self._bytes, self.camera_height)
        write_int32(self._bytes, self.sound_tag)

    def _read_map_layout(self, fobj):
        """ Load the map layout. """
        with Pointer(fobj):
            self.width, self.height = struct.unpack('<II', fobj.read(0x8))
            # ignore the number of entries as it is simply width * height
            _, offset = struct.unpack('<II', fobj.read(0x8))
            fobj.seek(offset)
            self.map_layout = list()
            for y in range(self.height):
                self.map_layout.append(list())
                for x in range(self.width):
                    self.map_layout[y].append(read_int32(fobj))
            self.map_layout = self.map_layout[::-1]

    def _write_map_layout_pointer(self):
        p = Pointer(self._bytes)
        p.assign_data(self._write_map_layout_info)
        self.pointer_data['headers'].append(p)
        write_int32(self._bytes, 0)

    def _write_map_layout_info(self, data):
        write_int32(data, self.width)
        write_int32(data, self.height)
        write_int32(data, self.height * self.width)
        p = Pointer(self._bytes)
        p.assign_data(self._write_map_layout)
        self.pointer_data['data'].append(p)
        write_int32(data, 0)

    def _write_map_layout(self, data):
        write_int32_array(data, self.map_layout)

    def _read_moving_platform_data(self, fobj):
        self.moving_platforms = list()
        for i in range(0x14):
            with Pointer(fobj):
                self.moving_platforms.append(MovingPlatform(fobj))

    def _write_moving_platform_data_pointers(self):
        for mp in self.moving_platforms:
            p = Pointer(self._bytes)
            p.assign_data(
                lambda _data, mp=mp: self._write_moving_platform_data(
                    _data, mp))
            self.pointer_data['headers'].append(p)
            write_int32(self._bytes, 0)

    def _write_moving_platform_data(self, data, mp):
        data.write(bytes(mp))

    def _read_movable_blocks(self, fobj):
        self.movable_blocks = list()
        for i in range(0x8):
            with Pointer(fobj):
                self.movable_blocks.append(MovableBlock(fobj))

    def _write_movable_blocks_pointers(self):
        for mb in self.movable_blocks:
            p = Pointer(self._bytes)
            p.assign_data(
                lambda _data, mb=mb: self._write_movable_blocks(_data, mb))
            self.pointer_data['headers'].append(p)
            write_int32(self._bytes, 0)

    def _write_movable_blocks(self, data, mb):
        data.write(bytes(mb))

    def _read_map_layers(self, fobj):
        """ Read all of the map layers into variables """
        for i in range(0x7):
            data = list()
            with Pointer(fobj):
                # skip the size
                fobj.seek(0x4, 1)
                with Pointer(fobj):
                    for y in range(self.height):
                        data.append(list())
                        for x in range(self.width):
                            data[y].append(read_int32(fobj))
            # flip the data verically
            data = data[::-1]
            # assign to a variable
            setattr(self, 'layer{0}_data'.format(str(i)), data)

    def _write_map_layers_pointer(self):
        for i in range(0x7):
            p = Pointer(self._bytes)
            layer_data = getattr(self, 'layer{0}_data'.format(str(i)))
            p.assign_data(
                lambda _data, layer_data=layer_data: self._write_map_layer_info(  # noqa
                    _data, layer_data))
            self.pointer_data['headers'].append(p)
            write_int32(self._bytes, 0)

    def _write_map_layer_info(self, data, layer_data):
        write_int32(data, self.height * self.width)
        p = Pointer(self._bytes)
        p.assign_data(
            lambda _data: self._write_map_layer(_data, layer_data))
        self.pointer_data['data'].append(p)
        write_int32(data, 0)

    def _write_map_layer(self, data, layer_data):
        write_int32_array(data, layer_data)

    def _read_gimmick_data(self, fobj):
        self.gimmick_data = list()
        with Pointer(fobj):
            count = read_int32(fobj)
            for i in range(count):
                gimmick_bytes = BytesIO(fobj.read(0x30))
                self.gimmick_data.append(gimmick_factory(gimmick_bytes))

    def _write_gimmick_data_pointer(self):
        p = Pointer(self._bytes)
        p.assign_data(lambda _data: self._write_gimmick_data(_data))
        self.pointer_data['headers'].append(p)
        write_int32(self._bytes, 0)

    def _write_gimmick_data(self, data):
        write_int32(data, len(self.gimmick_data))
        for gimmick in self.gimmick_data:
            data.write(bytes(gimmick))

    def _read_moving_platform_path_data(self, fobj):
        self.moving_platform_paths = list()
        with Pointer(fobj):
            count = read_int32(fobj)
            for i in range(count):
                with Pointer(fobj):
                    self.moving_platform_paths.append(MovingPlatformPath(fobj))

    def _write_moving_platform_path_data_pointer(self):
        p = Pointer(self._bytes)
        p.assign_data(lambda _data: self._write_moving_platform_path_data_info(
            _data))
        self.pointer_data['headers'].append(p)
        write_int32(self._bytes, 0)

    def _write_moving_platform_path_data_info(self, data):
        write_int32(data, len(self.moving_platform_paths))
        for mpp in self.moving_platform_paths:
            p = Pointer(self._bytes)
            p.assign_data(
                lambda _data, mpp=mpp: self._write_moving_platform_path_data(
                    _data, mpp))
            self.pointer_data['headers'].append(p)
            write_int32(data, 0)

    def _write_moving_platform_path_data(self, data, mpp):
        data.write(bytes(mpp))

    def __bytes__(self):
        # Write the header
        self.pointer_data = {'headers': list(), 'data': list()}
        self._bytes = BytesIO(b'')

        # Write each of the sections
        self._write_header()
        self._write_map_layout_pointer()
        self._write_moving_platform_data_pointers()
        self._write_movable_blocks_pointers()
        self._write_map_layers_pointer()
        self._write_gimmick_data_pointer()

        p = Pointer(self._bytes)
        p.assign_data(lambda _data: write_int32(_data, 0))
        self.pointer_data['headers'].append(p)
        write_int32(self._bytes, 0)
        self._write_moving_platform_path_data_pointer()

        # write all the pointer data. Do all headers then do data
        # swap entries 30 and 32 for some reason?!?
        self.pointer_data['headers'] = swap(self.pointer_data['headers'],
                                            30, 32)
        for pointer in self.pointer_data['headers']:
            pointer.write()

        for pointer in self.pointer_data['data']:
            pointer.write()

        # write the final file size
        self._bytes.seek(0x8)
        _bytes = self._bytes.getvalue()
        write_int32(self._bytes, len(_bytes))
        del _bytes
        return self._bytes.getvalue()


class MovingPlatform():
    def __init__(self, fobj):
        self.x_start, self.y_start = struct.unpack('<ii', fobj.read(0x8))
        self.x_end, self.y_end = struct.unpack('<ii', fobj.read(0x8))
        self.num_blocks = read_int32(fobj)
        self.data = list()
        for i in range(self.num_blocks):
            self.data.append(struct.unpack('<ii', fobj.read(0x8)))

    def __bytes__(self):
        _bytes = b''
        _bytes += struct.pack('<ii', self.x_start, self.y_start)
        _bytes += struct.pack('<ii', self.x_end, self.y_end)
        _bytes += struct.pack('<i', self.num_blocks)
        for data in self.data:
            _bytes += struct.pack('<ii', *data)
        return _bytes


class MovingPlatformPath():
    def __init__(self, fobj):
        count = read_int32(fobj)
        self.data = list()
        for i in range(count):
            self.data.append(struct.unpack('<iiiiiiii', fobj.read(0x20)))

    def __bytes__(self):
        _bytes = struct.pack('<i', len(self.data))
        for data in self.data:
            _bytes += struct.pack('<iiiiiiii', *data)
        return _bytes


class MovableBlock():
    def __init__(self, fobj):
        self.num_blocks = read_int32(fobj)
        self.block_locations = list()
        for i in range(self.num_blocks):
            self.block_locations.append(struct.unpack('<ii', fobj.read(0x8)))

    def __bytes__(self):
        _bytes = struct.pack('<i', self.num_blocks)
        for data in self.block_locations:
            _bytes += struct.pack('<ii', *data)
        return _bytes


def gimmick_factory(gimmick_bytes):
    # first, get the kind:
    gimmick_bytes.seek(0x4)
    kind = read_int32(gimmick_bytes)
    gimmick_bytes.seek(0)
    if kind == 2:
        return Gimmick_Door(gimmick_bytes)
    if kind == 3:
        return Gimmick_Laser(gimmick_bytes)
    if kind == 4:
        return Gimmick_Crown(gimmick_bytes)
    elif kind == 22:
        return Gimmick_Battery(gimmick_bytes)
    else:
        return Gimmick(gimmick_bytes)


class Gimmick():
    def __init__(self, fobj):
        self.param_fmts = ('<i', '<i', '<i', '<i', '<i', '<i')

        if fobj is None:
            return
        self.wuid = read_int32(fobj)
        self.kind = read_int32(fobj)
        self.x = read_int32(fobj)
        self.y = read_int32(fobj)
        self.group = read_int32(fobj)
        self.appearance = read_int32(fobj)

        self.load_parameters(fobj)

    @staticmethod
    def new(wuid, kind, x, y, group, appearance=0):
        if kind == 3:
            new_class = Gimmick_Laser(None)
            new_class.direction = 8  # up by default
        elif kind == 4:
            new_class = Gimmick_Crown(None)
        new_class.wuid = wuid
        new_class.kind = kind
        new_class.x = x
        new_class.y = y
        new_class.group = group
        new_class.appearance = appearance
        return new_class

    def load_parameters(self, fobj):
        self.param0 = read_int32(fobj)
        self.param1 = read_int32(fobj)
        self.param2 = read_int32(fobj)
        self.param3 = read_int32(fobj)
        self.param4 = read_int32(fobj)
        self.param5 = read_int32(fobj)

    def export(self, i):
        gimmick_data = etree.Element('Gimmick_{0}'.format(str(i)))
        wuid = etree.Element('wuid')
        wuid.text = str(self.wuid)
        gimmick_data.append(wuid)
        kind = etree.Element('kind')
        kind.text = str(self.kind)
        gimmick_data.append(kind)
        x = etree.Element('x')
        x.text = str(self.x)
        gimmick_data.append(x)
        y = etree.Element('y')
        y.text = str(self.y)
        gimmick_data.append(y)
        group = etree.Element('group')
        group.text = str(self.group)
        gimmick_data.append(group)
        appearance = etree.Element('appearance')
        appearance.text = str(self.appearance)
        gimmick_data.append(appearance)
        param0 = etree.Element('param0')
        param0.text = str(self.param0)
        gimmick_data.append(param0)
        param1 = etree.Element('param1')
        param1.text = str(self.param1)
        gimmick_data.append(param1)
        param2 = etree.Element('param2')
        param2.text = str(self.param2)
        gimmick_data.append(param2)
        param3 = etree.Element('param3')
        param3.text = str(self.param3)
        gimmick_data.append(param3)
        param4 = etree.Element('param4')
        param4.text = str(self.param4)
        gimmick_data.append(param4)
        param5 = etree.Element('param5')
        param5.text = str(self.param5)
        gimmick_data.append(param5)

    def image(self, data):
        return data.get(self.kind)

    def __bytes__(self):
        """ Serialize the Gimmick data. """
        data = BytesIO(b'')
        write_int32(data, self.wuid)
        write_int32(data, self.kind)
        write_int32(data, self.x)
        write_int32(data, self.y)
        write_int32(data, self.group)
        write_int32(data, self.appearance)

        for i, fmt in enumerate(self.param_fmts):
            if fmt == '<i':
                try:
                    write_int32(data, getattr(self, 'param{0}'.format(str(i))))
                except struct.error:
                    print(getattr(self, 'param{0}'.format(str(i))))
                    raise
            elif fmt == '<hh':
                write_tuple16(data, getattr(self, 'param{0}'.format(str(i))))

        return data.getvalue()

    def __getattr__(self, name):
        if 'param' in name:
            return 0
        else:
            raise AttributeError


class Gimmick_SpawnPoint(Gimmick):
    """ Gimmick # 0 """
    def __init__(self, fobj):
        super(Gimmick_SpawnPoint, self).__init__(fobj)


class Gimmick_Door(Gimmick):
    """ Gimmick # 2 """
    def __init__(self, fobj):
        super(Gimmick_Door, self).__init__(fobj)
        self.y += 32

    def __bytes__(self):
        self.y -= 32
        _bytes = super(Gimmick_Door, self).__bytes__()
        self.y += 32
        return _bytes


class Gimmick_Laser(Gimmick):
    """ Gimmick # 3 """
    def __init__(self, fobj):
        super(Gimmick_Laser, self).__init__(fobj)

    def image(self, data):
        return data[self.kind][self.direction]

    @property
    def direction(self):
        return self.param0

    @direction.setter
    def direction(self, value):
        self.param0 = value


class Gimmick_Crown(Gimmick):
    """ Gimmick # 4 """
    def __init__(self, fobj):
        super(Gimmick_Crown, self).__init__(fobj)


class Gimmick_Battery(Gimmick):
    """ Gimmick # 22 """
    def __init__(self, fobj):
        super(Gimmick_Battery, self).__init__(fobj)

    def load_parameters(self, fobj):
        self.polarity = self.param0 = read_int32(fobj)
        self.is_toggle = self.param1 = read_int32(fobj)
        self.target_id = self.param2 = read_int32(fobj)

    def image(self, data):
        return data[self.kind][self.polarity]


class Pointer():
    """ Context Manager to handle reading data located somewhere from a pointer
    """
    def __init__(self, fobj):
        self.fobj = fobj
        self.state = 'r'
        self.header_locations = dict()

        # start the pointer at the beginning of the file
        self.pointer_location = self.fobj.tell()
        self._bytes = BytesIO(b'')

        self.assign_func = None

    def __enter__(self):
        self.return_location = self.fobj.tell()
        offset = read_int32(self.fobj)
        self.fobj.seek(offset)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fobj.seek(self.return_location + 0x4)

    def assign_data(self, func):
        """ Call a function to assign data to the pointer. """
        self.assign_func = func

    def write(self):
        """ Write the bytes to the underlying data stream. """
        curr_offset = self.fobj.tell()
        self.assign_func(self.fobj)
        end_return = self.fobj.tell()
        self.fobj.seek(self.pointer_location)
        write_int32(self.fobj, curr_offset)
        self.fobj.seek(end_return)


def swap(lst, idx1, idx2):
    a = lst.pop(idx1)
    b = lst.pop(idx2 - 1)
    lst.insert(idx1, b)
    lst.insert(idx2, a)
    return lst
