# serialise/deserialise the .bbmap files which are the uncompressed versions of the archive.bin.cmp files found in level folders

import struct
import io

from bbmap import main

class BBCompiler():
    def __init__(self, file_in, file_out):
        self.file_in = file_in
        self.file_out = file_out

        self.main_struct = main()

        self.file = open(self.file_in, 'rb')
        BD = io.BufferedReader(self.file)
        for key in self.main_struct.data:
            fmt = self.main_struct.data[key]
            try:
                l = struct.calcsize(fmt)
                # if the code hasn't broken by this point then the data is just a format for the struct class
                print("{0}: {1}".format(key, struct.unpack(fmt, BD.read(l))[0]))        # need the [0] as this will always return a tuple
            except:
                l = len(fmt)
                for subkey in fmt.data:
                    sublen = struct.calcsize(fmt.data[subkey])
                    print("{0}: {1}".format(subkey, struct.unpack(fmt.data[subkey], BD.read(sublen))[0]))        # need the [0] as this will always return a tuple
        self.file.close()

a = BBCompiler('1-1.bbmap', None)

            
