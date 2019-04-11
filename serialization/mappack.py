import struct
import os
import shutil
import os.path as op
import re

import subprocess


def unpack_map(fname):
    """Extract all the stepXX.bin's from an Archive.bin

    Parameters
    ----------
    fname : str or path-like object
        The full path to the Archive.bin
    """

    # check to see if the file is compressed (ie. has the .cmp extension)
    if op.splitext(fname)[1] == '.cmp':
        # in this case decompress it...
        # because the script overwrites the file we need to make a copy.
        shutil.copyfile(fname, '{}_copy'.format(fname))
        # now run lzx.exe on the file to decompress it
        cmds = ['tools\\lzx.exe', '-d', fname]
        subprocess.run(cmds, stdout=subprocess.PIPE)
        os.rename(fname, op.splitext(fname)[0])
        os.rename('{}_copy'.format(fname), fname)
        # set the filename to be used for the rest of the function as the
        # decompressed file
        fname = op.splitext(fname)[0]

    arcfile = open(fname, 'rb')

    # Read the Magic number/version(?)
    if arcfile.read(8) != b'XBIN\x34\x12\x02\x00':
        raise TypeError('Provided file is not a valid XBIN archive')

    # read the file size:
    filesize, = struct.unpack('<L', arcfile.read(4))
    assert filesize == op.getsize(fname)

    # skip some unknown value (should be \xE9\xFD\x00\x00)
    arcfile.seek(4, 1)

    filenum, = struct.unpack('<L', arcfile.read(4))

    # bounds: list of tuples of form: (fname data start, data start)
    bounds = []

    for _ in range(filenum):
        bounds.append(struct.unpack('<LL', arcfile.read(8)))
    # copy the last entry to make the following algorithm easier...
    bounds.append(bounds[-1])

    for i in range(filenum):
        # first, get file name...
        arcfile.seek(bounds[i][0])
        fname_length, = struct.unpack('<L', arcfile.read(4))
        fname = struct.unpack('{0}s'.format(fname_length),
                              arcfile.read(fname_length))[0].decode()
        # Now, get the data itself.
        # Just to where the data starts
        arcfile.seek(bounds[i][1])
        # we'll just make sure it is XBIN data:
        if arcfile.read(8) != b'XBIN\x34\x12\x02\x00':
            raise TypeError('Provided file is not a valid XBIN archive')
        # read the length of the data:
        data_length, = struct.unpack('<L', arcfile.read(4))
        # jump back to the start of the data chunk
        arcfile.seek(bounds[i][1])
        # then read the correct amount of data into a new file with the
        # appropriate name.
        full_path = op.join(op.dirname(fname), fname)
        with open(full_path, 'wb') as f:
            f.write(arcfile.read(data_length))

        return full_path


def pack_map(fpath, recompress=True):
    """
    Search a directory for all files of the form stepXX.bin and repack into
    a Archive.bin file.

    Parameters
    ----------
    fpath : str or path-like object
        The folder path to search for stepXX.bin files to repack into the
        Archive.bin file.
    recompress : bool
        Whether or not to recompress the resultant Archive.bin.
    """
    # find all the files of the form stepXX.bin:
    fnames = []
    for fname in os.listdir(fpath):
        if re.match('step[0-9]{2}.bin', fname):
            fnames.append(op.join(fpath, fname))
    fnames.sort()

    # we need to get some data first before rebuilding the file.
    # first, we need the total file size...
    fsize = 0x14    # minimal header size (with 0 other things in it)
    for fname in fnames:
        fsize += op.getsize(fname)
        # add 8 on for each one to account for the data in the header
        fsize += 0x8
        # add on the length of the file name plus the 4 bytes before and after
        fsize += 0x4 + len(op.basename(fname)) + 0x4
    # finally, if there is more than one file in the list, add 1 less than that
    # 0x2 padding's because there is 0x6 padding between the names, not 0x4
    fsize += (len(fnames) - 1) * 0x2

    # now write all the data to the Archive.bin file
    full_path = op.join(fpath, 'Archive2.bin')
    with open(full_path, 'wb') as f:
        f.write(b'XBIN\x34\x12\x02\x00')    # magic
        f.write(struct.pack('<LLL', fsize, 0xFDE9, len(fnames)))
        fname_pointers = []
        fname_locations = []
        data_pointers = []
        data_locations = []
        for _ in range(len(fnames)):
            # write some empty data
            fname_pointers.append(f.tell())
            data_pointers.append(f.tell() + 0x4)
            f.write(struct.pack('<LL', 0, 0))

        # for each file, read the data in and make note of where it all goes
        for fname in fnames:
            with open(fname, 'rb') as stepfile:
                data_locations.append(f.tell())
                f.write(stepfile.read())
        # next, write all the names back into the file
        for i, fname in enumerate(fnames):
            shortname = op.basename(fname)
            fname_locations.append(f.tell())
            f.write(struct.pack('<L', len(shortname)))
            f.write(struct.pack('{0}s'.format(len(shortname)),
                                shortname.encode()))
            f.write(struct.pack('<L', 0))
            if len(fnames) != 1 and i != len(fnames) - 1:
                f.write(struct.pack('<H', 0))

        # finally update the pointer info
        assert (len(fname_pointers) == len(fname_locations) ==
                len(data_pointers) == len(data_locations))
        for i in range(len(fname_pointers)):
            f.seek(fname_pointers[i])
            f.write(struct.pack('<L', fname_locations[i]))
            f.seek(data_pointers[i])
            f.write(struct.pack('<L', data_locations[i]))

    if recompress:
        shutil.copyfile(full_path, '{}_copy'.format(full_path))
        # now run lzx.exe on the file to decompress it
        cmds = ['tools\\lzx.exe', '-evb', full_path]
        subprocess.run(cmds, stdout=subprocess.PIPE)
        os.rename(full_path, '{0}.cmp'.format(full_path))
        os.rename('{}_copy'.format(full_path), full_path)


if __name__ == "__main__":
    # unpack_map('Archive.bin.cmp')
    pack_map('.')
