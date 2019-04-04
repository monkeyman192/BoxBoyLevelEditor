import struct


def read_dtype(fobj, dtype):
    if dtype == '<i':
        return read_int32(fobj)
    elif dtype == '<hh':
        return read_tuple16(fobj)


def read_int32(fobj):
    return struct.unpack('<i', fobj.read(0x4))[0]


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
