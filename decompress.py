from os import walk, rename
import os.path as op
import subprocess


def decompress_folder(_path):
    for root, _, files in walk(_path):
        for file in files:
            path = op.join(root, file)
            if op.splitext(path)[1] == '.cmp':
                cmds = ['tools\\lzx.exe', '-d', path]
                subprocess.run(cmds)
                rename(path, op.splitext(path)[0])


def extract_maps(_path):
    for root, _, files in walk(_path):
        for file in files:
            path = op.join(root, file)
            if op.splitext(path)[1] == '.bin':
                f = open(path, 'rb')
                if f.read(4) == b'XBIN':
                    cmds = ['python', 'ae.py', path]
                    subprocess.run(cmds)


if __name__ == "__main__":
    decompress_folder('D:\\3ds\\3ds hacking\\Games\\Extracted_from_3ds\\BoxBoy!\\Original\\romfs\\gfx')
    print('decompressed')
    #extract_maps('romfs')
    #print('extracted')
