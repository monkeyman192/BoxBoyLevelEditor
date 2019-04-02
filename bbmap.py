# main struct for the bbmap files

from collections import OrderedDict
import struct


class bbmap():
    # this is the base class all other structs will be subclassed from,
    # containing basic properties
    def __init__(self):
        self.data = OrderedDict()

    def __len__(self):
        i = 0
        for key in self.data:
            try:
                i += struct.calcsize(self.data[key])
            except:
                i += len(self.data[key])
        return i


class main(bbmap):
    def __init__(self):
        super(main, self).__init__()        # initialise the parent class

        self.name = 'MainData'

        # actual structure
        self.data['Magic'] = '4s'                                        # 0x00
        self.data['Version'] = '<I'                                      # 0x04
        self.data['Filesize'] = '<I'                                     # 0x08
        self.data['Unknown2'] = '<I'                                     # 0x0C
        self.data['BoxNum'] = '<I'                                       # 0x10
        self.data['BoxSetNum'] = '<I'                                    # 0x14
        self.data['CameraHeight'] = '<I'                                 # 0x18
        self.data['SoundTag'] = '<I'                                     # 0x1C
        self.data['UnknownPositions'] = List(Vector2i(), 'Position', 20) # 0x20
        self.data['Unknown3'] = '<I'
        self.data['Unknown4'] = '<I'
        self.data['Unknown5'] = '<I'
        self.data['UnknownStruct'] = List(UnknownStruct(), 'Entry', 20)
        self.data['Padding_maybe'] = '32s'
        self.data['AnotherPosition0'] = Vector2i()
        self.data['AnotherPosition1'] = Vector2i()
        self.data['AnotherPosition2'] = Vector2i()
        self.data['AnotherPosition3'] = Vector2i()
        self.data['AnotherPosition4'] = Vector2i()
        self.data['AnotherPosition5'] = Vector2i()
        self.data['AnotherPosition6'] = Vector2i()
        self.data['Gimmicks'] = Gimmick()


"""
From 0x20:
A list of absolute positions to some data.
The first 2 values of each entry is the x-width and y-height of it?
The values seem a lot larger than the actual map but I think it is just to
include a region around the map.

1st structure is 0x10 long.
This structure has the format:
 - <I : width
 - <I : height
 - <I : area (width * height)
 - <I : offset to the solid blocks
 In this data section the following blocks have the following meaning:
  - 0x00 : empty space
  - 0x01 : solid ground
  - 0x05 : camera wall
Then there are 20 structures that are 0x14 long + extra depending on the byte
at + 0x10 relative to within this struct.
The first 4 values are:
 - <I : x_initial
 - <I : y_initial
 - <I : x_final
 - <I : y_final
The byte at +0x10 has meaning:
 - 0x00 : nothing
 - 0x04 : Number of moving boxes in group
 {
     0x8 bytes.
     not sure what...
 }
After this are 8 pointers to data to describe push-able blocks.
The data has the structure:
 - <I : number of blocks:
  {
      - <I : x position
      - <I : y position
  } x number of blocks
After this there are 7 pointers to data that have length 0x8.
Each of these data chunks has the format:
<I : 0x4 : number of data points (size = number x 4)
<I : 0x4 : data offset
First number (number of data points is equal to the product of the first 2
dimensions in the first structure (the one that is 0x10 long))
After this are 3 more pointers which do something I don't know...
First pointer (at 0xB0) is the gimmick data.
This has the format:
+ 0x00 : <I : number of elements in the list
+ 0x04 : n * GimmickData() structs, each 0x30 long.

The 2nd last pointer always seems to point to data that is empty, but the last
pointer points to data relating to the moving blocks also.
This has the structure:
 - <I : number of data sections
 {
     - <I offset to data
 } x number of blocks
Each block has the structure:
 - <I : number of chunks:
 {
     0x20 bytes of something??
 }

"""


class List(bbmap):
    # basically a list wrapper
    def __init__(self, dtype, sub_name, *size):
        # size is only specified if the list starts as a pre-defined size
        super(List, self).__init__()

        self.name = 'List'

        self.sub_name = sub_name

        self.dtype = dtype
        if size:
            self.size = size[0]
        else:
            self.size = None

        if self.size is not None:
            for i in range(self.size):
                self.data['{0}_{1}'.format(self.sub_name, i)] = self.dtype

    def set_size(self, size):
        self.size = size
        for i in range(self.size):
            self.data['{0}_{1}'.format(self.sub_name, i)] = self.dtype


class Vector2i(bbmap):
    def __init__(self):
        super(Vector2i, self).__init__()

        self.name = 'Vector2i'

        self.data['x'] = '<I'
        self.data['y'] = '<I'


class Gimmick(bbmap):
    def __init__(self):
        super(Gimmick, self).__init__()

        self.name = 'Gimmick'

        self.data['GimmickCount'] = '<I'
        self.data['GimmickData'] = List(GimmickData(), 'Gimmick')
        """self.data['Gimmick0'] = GimmickData()
        self.data['Gimmick1'] = GimmickData()
        self.data['Gimmick2'] = GimmickData()
        self.data['Gimmick3'] = GimmickData()
        self.data['Gimmick4'] = GimmickData()
        self.data['Gimmick5'] = GimmickData()
        self.data['Gimmick6'] = GimmickData()
        self.data['Gimmick7'] = GimmickData()
        self.data['Gimmick8'] = GimmickData()
        self.data['Gimmick9'] = GimmickData()"""


class GimmickData(bbmap):
    def __init__(self):
        super(GimmickData, self).__init__()

        self.name = 'GimmickData'

        # struct size: 0x30

        self.data['wuid'] = '<I'        # 0x00
        self.data['kind'] = '<I'        # 0x04
        self.data['x'] = '<I'           # 0x08
        self.data['y'] = '<I'           # 0x0C
        self.data['group'] = '<I'       # 0x10
        self.data['appearance'] = '<I'  # 0x14
        self.data['param0'] = '<I'      # 0x18
        self.data['param1'] = '<I'      # 0x1C
        self.data['param2'] = '<I'      # 0x20
        self.data['param3'] = '<I'      # 0x24
        self.data['param4'] = '<I'      # 0x28
        self.data['param5'] = '<I'      # 0x2C


class FallBlock(bbmap):
    def __init__(self):
        super(FallBlock, self).__init__()

        self.name = 'FallBlock'

        self.data['gridCount'] = '<I'
        self.data['grid'] = FallBlockGridData()


class FallBlockGridData(bbmap):
    def __init__(self):
        super(FallBlockGridData, self).__init__()

        self.name = 'FallBlockGridData'

        self.data['x'] = '<I'
        self.data['y'] = '<I'


class Enemies(bbmap):
    def __init__(self):
        super(Enemies, self).__init__()

        self.name = 'Enemies'

        self.data['count'] = '<I'
        self.data['Enemies'] = EnemyData()


class EnemyData(bbmap):
    def __init__(self):
        super(EnemyData, self).__init__()

        self.name = 'EnemyData'

        # struct size: 0x18

        self.data['kind'] = '<I'            # 0x00
        self.data['maproPos'] = Vector2i    # 0x04
        self.data['level'] = '<I'           # 0x0C
        self.data['dirType'] = '<I'         # 0x10
        self.data['variation'] = '<I'       # 0x14


class UnknownStruct(bbmap):
    def __init__(self):
        super(UnknownStruct, self).__init__()

        self.name = 'UnknownStruct'

        self.data['Unknown0'] = '<I'
        self.data['Unknown1'] = '<I'
        self.data['Unknown2'] = '<I'
        self.data['Unknown3'] = '<I'
        self.data['Unknown4'] = '<I'


class LandColl(bbmap):
    def __init__(self):
        super(LandColl, self).__init__()

        self.name = 'LandColl'

        self.data['width'] = '<I'
        self.data['height'] = '<I'
