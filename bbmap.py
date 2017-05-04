# main struct for the bbmap files

from collections import OrderedDict
import struct


class bbmap():
    # this is the base class all other structs will be subclassed from, containing basic properties
    def __init__(self):
        self.data = OrderedDict()

    def __len__(self):
        l = 0
        for key in self.data:
            try:
                l += struct.calcsize(self.data[key])
            except:
                l += len(self.data[key])
        return l

    """
    def deserialise(self):
        # main routine that will handle the deserialising.
        self.deserialised_data = OrderedDict()
        for key in self.data:
            try:
                self.deserialised_data[key] = self.data[key].deserialise()
            except:
                self.deserialised_data[key] = self.data[key]
        return self.deserialised_data
    """
                

class main(bbmap):
    def __init__(self):
        super(main, self).__init__()        # initialise the parent class

        # actual structure
        self.data['InitialPadding'] = '28s'        # just going to ignore the first 0x1C bytes...
        self.data['Magic'] = '4s'
        self.data['Version'] = '<I'
        self.data['Unknown1'] = '<I'
        self.data['Unknown2'] = '<I'
        self.data['BoxNum'] = '<I'
        self.data['BoxSetNum'] = '<I'
        self.data['CameraHeight'] = '<I'
        self.data['SoundTag'] = '<I'
        self.data['position0'] = Vector2i()
        self.data['position1'] = Vector2i()
        self.data['position2'] = Vector2i()
        self.data['position3'] = Vector2i()
        self.data['position4'] = Vector2i()
        self.data['position5'] = Vector2i()
        self.data['position6'] = Vector2i()
        self.data['position7'] = Vector2i()
        self.data['position8'] = Vector2i()
        self.data['position9'] = Vector2i()
        self.data['position10'] = Vector2i()
        self.data['position11'] = Vector2i()
        self.data['position12'] = Vector2i()
        self.data['position13'] = Vector2i()
        self.data['position14'] = Vector2i()
        self.data['position15'] = Vector2i()
        self.data['position16'] = Vector2i()
        self.data['position17'] = Vector2i()
        self.data['position18'] = Vector2i()
        self.data['position19'] = Vector2i()
        self.data['Unknown3'] = '<I'
        self.data['Unknown4'] = '<I'
        self.data['Unknown5'] = '<I'
        self.data['UnknownStruct0'] = UnknownStruct()
        self.data['UnknownStruct1'] = UnknownStruct()
        self.data['UnknownStruct2'] = UnknownStruct()
        self.data['UnknownStruct3'] = UnknownStruct()
        self.data['UnknownStruct4'] = UnknownStruct()
        self.data['UnknownStruct5'] = UnknownStruct()
        self.data['UnknownStruct6'] = UnknownStruct()
        self.data['UnknownStruct7'] = UnknownStruct()
        self.data['UnknownStruct8'] = UnknownStruct()
        self.data['UnknownStruct9'] = UnknownStruct()
        self.data['UnknownStruct10'] = UnknownStruct()
        self.data['UnknownStruct11'] = UnknownStruct()
        self.data['UnknownStruct12'] = UnknownStruct()
        self.data['UnknownStruct13'] = UnknownStruct()
        self.data['UnknownStruct14'] = UnknownStruct()
        self.data['UnknownStruct15'] = UnknownStruct()
        self.data['UnknownStruct16'] = UnknownStruct()
        self.data['UnknownStruct17'] = UnknownStruct()
        self.data['UnknownStruct18'] = UnknownStruct()
        self.data['UnknownStruct19'] = UnknownStruct()
        self.data['Padding_maybe'] = '32s'
        self.data['AnotherPosition0'] = Vector2i()
        self.data['AnotherPosition1'] = Vector2i()
        self.data['AnotherPosition2'] = Vector2i()
        self.data['AnotherPosition3'] = Vector2i()
        self.data['AnotherPosition4'] = Vector2i()
        self.data['AnotherPosition5'] = Vector2i()
        self.data['AnotherPosition6'] = Vector2i()
        self.data['Gimmicks'] = Gimmick()
        
        

class Vector2i(bbmap):
    def __init__(self):
        super(Vector2i, self).__init__()

        self.data['x'] = '<I'
        self.data['y'] = '<I'

class Gimmick(bbmap):
    def __init__(self):
        super(Gimmick, self).__init__()

        self.data['count'] = '<I'
        self.data['Gimmick0'] = GimmickData()
        self.data['Gimmick1'] = GimmickData()
        self.data['Gimmick2'] = GimmickData()
        self.data['Gimmick3'] = GimmickData()
        self.data['Gimmick4'] = GimmickData()
        self.data['Gimmick5'] = GimmickData()
        self.data['Gimmick6'] = GimmickData()
        self.data['Gimmick7'] = GimmickData()
        self.data['Gimmick8'] = GimmickData()
        self.data['Gimmick9'] = GimmickData()

class GimmickData(bbmap):
    def __init__(self):
        super(GimmickData, self).__init__()

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

        self.data['gridCount'] = '<I'
        self.data['grid'] = FallBlockGridData()

class FallBlockGridData(bbmap):
    def __init__(self):
        super(FallBlockGridData, self).__init__()

        self.data['x'] = '<I'
        self.data['y'] = '<I'

class Enemies(bbmap):
    def __init__(self):
        super(Enemies, self).__init__()

        self.data['count'] = '<I'
        self.data['Enemies'] = EnemyData()

class EnemyData(bbmap):
    def __init__(self):
        super(EnemyData, self).__init__()

        # struct size: 0x18

        self.data['kind'] = '<I'            # 0x00
        self.data['maproPos'] = Vector2i    # 0x04
        self.data['level'] = '<I'           # 0x0C
        self.data['dirType'] = '<I'         # 0x10
        self.data['variation'] = '<I'       # 0x14

class UnknownStruct(bbmap):
    def __init__(self):
        super(UnknownStruct, self).__init__()

        self.data['Unknown0'] = '<I'
        self.data['Unknown1'] = '<I'
        self.data['Unknown2'] = '<I'
        self.data['Unknown3'] = '<I'
        self.data['Unknown4'] = '<I'
