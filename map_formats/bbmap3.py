""" Map format for Bye-Bye BoxBoy! """
__author__ = "monkeyman192"

import struct
import json

from serialization.io import read_int32, read_byte, Pointer, read_float32


# types:
# 1: value
# 3: boolean
# 4: string
# 5: named pointer array
# 6: pointer array

class BBMap():
    def __init__(self, fpath):
        self.fpath = fpath

        with open(self.fpath, 'rb') as fobj:
            self._read_header(fobj)
            data = self._read_data(fobj)
        with open('data.json', 'w') as fobj:
            json.dump(data, fobj, indent=4)

    def _read_header(self, fobj):
        self.magic = struct.unpack('4s', fobj.read(0x4))[0]
        if not self.magic == b'XBIN':
            raise ValueError('Provided file is not a valid BoxBoy map file')
        self.unknown_value0 = read_int32(fobj)
        self.filesize = read_int32(fobj)
        self.unknown_value1 = read_int32(fobj)
        self.rloc_loc = read_int32(fobj)
        self.yaml_check = struct.unpack('4s', fobj.read(0x4))[0]
        if not self.yaml_check == b'YAML':
            raise ValueError('Provided file is not a valid BoxBoy 3 map file')
        self.yaml_version = read_int32(fobj)

    def _read_data(self, fobj):
        # print('reading data at {0}'.format(hex(fobj.tell())))
        dtype = read_int32(fobj)
        if dtype == 1:
            # read an int
            data = read_int32(fobj)  # maybe different dtypes?
        elif dtype == 2:
            # read a float
            data = read_float32(fobj)
        elif dtype == 3:
            # read a boolean values
            data = bool(read_byte(fobj))
        elif dtype == 4:
            # Pointer to byte array?
            data = list()
            with Pointer(fobj):
                data = self._read_name(fobj).decode('utf')
        elif dtype == 5:
            data = list()
            count = read_int32(fobj)
            for _ in range(count):
                with Pointer(fobj):
                    name = self._read_name(fobj).decode('utf')
                with Pointer(fobj):
                    new_data = self._read_data(fobj)
                data.append({name: new_data})
        elif dtype == 6:
            data = list()
            count = read_int32(fobj)
            for _ in range(count):
                with Pointer(fobj):
                    data.append(self._read_data(fobj))
        else:
            print(dtype, hex(fobj.tell()))
            data = None
        return data

    def _read_name(self, fobj):
        _len = read_int32(fobj)
        return struct.unpack('{0}s'.format(str(_len)), fobj.read(_len))[0]


if __name__ == '__main__':
    m = BBMap('Costume.bin')
