import struct
from io import BytesIO


def read_name(fobj):
    _len = read_int32(fobj)
    return struct.unpack('{0}s'.format(str(_len)), fobj.read(_len))[0]


def read_dtype(fobj, dtype):
    if dtype == '<i':
        return read_int32(fobj)
    elif dtype == '<hh':
        return read_tuple16(fobj)


def read_byte(fobj):
    return struct.unpack('<B', fobj.read(0x1))[0]


def read_int32(fobj):
    return struct.unpack('<i', fobj.read(0x4))[0]


def read_float32(fobj):
    return struct.unpack('<f', fobj.read(0x4))[0]


def read_tuple16(fobj):
    return struct.unpack('<hh', fobj.read(0x4))


def write_int32(fobj, data):
    try:
        fobj.write(struct.pack('<i', data))
    except struct.error:
        print(data)
        raise


def write_tuple16(fobj, data):
    fobj.write(struct.pack('<hh', data[0], data[1]))


def write_int32_array(fobj, data):
    # flip the data
    d = data[::-1]
    for row in d:
        for value in row:
            write_int32(fobj, value)


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
