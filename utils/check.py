import struct
import os

for root, folders, files in os.walk('G:\\3ds\\3ds hacking\\Games\\Extracted_from_3ds\\BoxBoy!\\Modified\\romfs\\map'):
    for fname in files:
        if fname == 'step01.bin':
            with open(os.path.join(root, fname), 'rb') as f:
                f.seek(0xB4)
                offset = struct.unpack('<I', f.read(0x4))[0]
                f.seek(offset)
                data1 = struct.unpack('<I', f.read(0x4))[0]
                f.seek(0xB8)
                offset = struct.unpack('<I', f.read(0x4))[0]
                f.seek(offset)
                data2 = struct.unpack('<I', f.read(0x4))[0]
            if data1 != 0 or data2 != 0:
                print(os.path.join(root, fname))