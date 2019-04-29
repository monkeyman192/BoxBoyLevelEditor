# experimental function to extract data from mint archives
__author__ = "monkeyman192"

import os.path as op
import os
import struct
from serialization.io import read_int32, Pointer, read_name

# for BB3: named pointer locations start at 0x18F8
# at +0x1C is the pointer to the start of the named pointers

BASEPATH = 'Archive'


class Mint():
    def __init__(self, fpath):
        self.fpath = fpath

        with open(self.fpath, 'rb') as fobj:
            self._read_header(fobj)
            self._read_data(fobj)

    def _read_header(self, fobj):
        self.magic = struct.unpack('4s', fobj.read(0x4))[0]
        if not self.magic == b'XBIN':
            raise ValueError('Provided file is not a valid BoxBoy map file')
        self.version = read_int32(fobj)
        self.filesize = read_int32(fobj)
        self.unknown_value1 = read_int32(fobj)

    def _read_data(self, fobj):
        fobj.seek(0x1C)
        count = read_int32(fobj)
        with Pointer(fobj):
            for _ in range(count):
                with Pointer(fobj):
                    name = read_name(fobj).decode('utf')
                    print(name)
                with Pointer(fobj):
                    self._extract_xbin(fobj, name)

    def _extract_xbin(self, fobj, name):
        entry_pt = fobj.tell()
        magic = struct.unpack('4s', fobj.read(0x4))[0]
        if not magic == b'XBIN':
            return
        read_int32(fobj)
        filesize = read_int32(fobj)
        fobj.seek(entry_pt)
        data = fobj.read(filesize)
        fpath = op.join(BASEPATH, *name.split('.')) + '.xbin'
        if not op.exists(op.dirname(fpath)):
            os.makedirs(op.dirname(fpath))
        with open(fpath, 'wb') as fobj:
            fobj.write(data)


class Xbin():
    def __init__(self, fpath):
        self.fpath = fpath

        with open(self.fpath, 'rb') as fobj:
            self._read_header(fobj)

    def _read_header(self, fobj):
        data = ''
        self.magic = struct.unpack('4s', fobj.read(0x4))[0]             # 0x00
        if not self.magic == b'XBIN':
            raise ValueError('Provided file is not a valid BoxBoy map file')
        self.version = read_int32(fobj)                                 # 0x04
        self.filesize = read_int32(fobj)                                # 0x08
        self.unknown_value0 = read_int32(fobj)                          # 0x0C
        with Pointer(fobj):                                             # 0x10
            self.filename = read_name(fobj)
        self.unknown_value1 = read_int32(fobj)                          # 0x14
        with Pointer(fobj):                                             # 0x18
            count = read_int32(fobj)
            self.unknown_bytes = fobj.read(count * 4)
        with Pointer(fobj):                                             # 0x1C
            count = read_int32(fobj)
            for _ in range(count):
                with Pointer(fobj):
                    with Pointer(fobj):
                        attribute = read_name(fobj)
                        data += attribute.decode('utf') + '\n'
                    read_int32(fobj)
                    read_int32(fobj)
                    read_int32(fobj)
                    with Pointer(fobj):
                        count = read_int32(fobj)
                        for _ in range(count):
                            with Pointer(fobj):
                                with Pointer(fobj):
                                    enum_name = read_name(fobj).decode(
                                        'utf')
                                enum_value = read_int32(fobj)
                                data += (str(enum_name) + '\t' +
                                         str(enum_value) + '\n')
            if len(data) != 0:
                with open(self.fpath.replace('xbin', 'txt'), 'w') as f:
                    f.write(data)
