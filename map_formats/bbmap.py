""" Map format for BoxBoy! and BoxBoxBoy! """
__author__ = "monkeyman192"

import struct
from io import BytesIO
import shutil

from serialization.io import (read_int32, write_int32, write_int32_array,
                              Pointer)
from gimmicks.Gimmicks import gimmick_factory


class BBMap():
    def __init__(self, fpath):
        self.fpath = fpath

        with open(fpath, 'rb') as fobj:
            self._read_header(fobj)
            self._read_map_layout(fobj)
            self._read_moving_platform_data(fobj)
            self._read_pushblocks(fobj)
            self._read_map_layers(fobj)
            self._read_gimmick_data(fobj)
            # skip whatever the next pointer goes to as it is always empty...
            fobj.seek(0x4, 1)
            self._read_moving_platform_path_data(fobj)

    def save(self):
        """ Export all the data. """
        data = bytes(self)
        shutil.copy(self.fpath, self.fpath + '_orig')
        with open(self.fpath, 'wb') as f:
            f.write(data)

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
                for _ in range(self.width):
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
        for _ in range(0x14):
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

    def _read_pushblocks(self, fobj):
        self.pushblocks = list()
        for _ in range(0x8):
            with Pointer(fobj):
                self.pushblocks.append(PushBlock(fobj))

    def _write_pushblocks_pointers(self):
        for pb in self.pushblocks:
            p = Pointer(self._bytes)
            p.assign_data(
                lambda _data, pb=pb: self._write_pushblocks(_data, pb))
            self.pointer_data['headers'].append(p)
            write_int32(self._bytes, 0)

    def _write_pushblocks(self, data, pb):
        data.write(bytes(pb))

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
                        for _ in range(self.width):
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
            for _ in range(count):
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
            for _ in range(count):
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
        self._write_pushblocks_pointers()
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
        for _ in range(self.num_blocks):
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
        for _ in range(count):
            self.data.append(struct.unpack('<iiiiiiii', fobj.read(0x20)))

    def __bytes__(self):
        _bytes = struct.pack('<i', len(self.data))
        for data in self.data:
            _bytes += struct.pack('<iiiiiiii', *data)
        return _bytes


class PushBlock():
    def __init__(self, fobj):
        self.num_blocks = read_int32(fobj)
        self.block_locations = list()
        for _ in range(self.num_blocks):
            self.block_locations.append(struct.unpack('<ii', fobj.read(0x8)))

    def __bytes__(self):
        _bytes = struct.pack('<i', len(self.block_locations))
        for data in self.block_locations:
            _bytes += struct.pack('<ii', *data)
        return _bytes


def swap(lst, idx1, idx2):
    a = lst.pop(idx1)
    b = lst.pop(idx2 - 1)
    lst.insert(idx1, b)
    lst.insert(idx2, a)
    return lst
