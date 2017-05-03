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
        self.data['Initial Padding'] = '28s'        # just going to ignore the first 0x1C bytes...
        self.data['Magic'] = '4s'
        self.data['Version'] = '<I'
        self.data['Unknown 1'] = '<I'
        self.data['Unknown 2'] = '<I'
        self.data['BoxNum'] = '<I'
        self.data['BoxSetNum'] = '<I'
        self.data['CameraHeight'] = '<I'
        self.data['SoundTag'] = '<I'
        self.data['pos1'] = Vector2i()

class Vector2i(bbmap):
    def __init__(self):
        super(Vector2i, self).__init__()

        self.data['x'] = '<I'
        self.data['y'] = '<I'
