from serialization.io import read_int32, write_int32
from io import BytesIO


def event_factory(event_bytes):
    # First, get the kind:
    event_bytes.seek(0x4)
    kind = read_int32(event_bytes)
    event_bytes.seek(0)
    if kind == 0:
        return Event_OnEnterScene(event_bytes)
    elif kind == 6:
        return Event_Wait(event_bytes)
    elif kind == 13:
        return Event_MoveLandInit(event_bytes)
    elif kind == 14:
        return Event_MoveLandCmd(event_bytes)
    elif kind == 17:
        return Event_Flag(event_bytes)
    elif kind == 18:
        return Event_ToFlag(event_bytes)
    elif kind == 19:
        return Event_DamageMoveLandInit(event_bytes)


class Event():
    def __init__(self, fobj=None):
        try:
            self.param_names
        except AttributeError:
            self.param_names = ('param0', 'param1', 'param2', 'param3',
                                'param4', 'param5')

        if fobj is None:
            return

        self.wuid = read_int32(fobj)
        self.kind = read_int32(fobj)

        self.load_parameters(fobj)
        self.name = str(self.kind)

    def load_parameters(self, fobj):
        self.param0 = read_int32(fobj)
        self.param1 = read_int32(fobj)
        self.param2 = read_int32(fobj)
        self.param3 = read_int32(fobj)
        self.param4 = read_int32(fobj)
        self.param5 = read_int32(fobj)

    @staticmethod
    def new(wuid, kind):
        if kind == 0:
            new_class = Event_OnEnterScene()
        elif kind == 6:
            new_class = Event_Wait()
        elif kind == 13:
            new_class = Event_MoveLandInit()
        elif kind == 14:
            new_class = Event_MoveLandCmd()
        elif kind == 17:
            new_class = Event_Flag()
        elif kind == 18:
            new_class = Event_ToFlag()
        elif kind == 19:
            new_class = Event_DamageMoveLandInit()
        else:
            new_class = Event()
        new_class.wuid = wuid
        new_class.kind = kind

        return new_class

    def __bytes__(self):
        """ Serialize the Event data. """
        data = BytesIO(b'')
        write_int32(data, self.wuid)
        write_int32(data, self.kind)
        write_int32(data, self.param0)
        write_int32(data, self.param1)
        write_int32(data, self.param2)
        write_int32(data, self.param3)
        write_int32(data, self.param4)
        write_int32(data, self.param5)
        return data.getvalue()

    def __str__(self):
        # This is a bit verbose but is mainly just for testing right now...
        out_str = '<{0}>\t'.format(self.name)
        for pname in self.param_names:
            out_str += pname + ':\t' + str(getattr(self, pname)) + '\t'
        return out_str


class Event_OnEnterScene(Event):
    """ Event # 0 """
    def __init__(self, fobj=None):
        super(Event_OnEnterScene, self).__init__(fobj)
        self.name = 'OnEnterScene'


class Event_Wait(Event):
    """ Event # 6 """
    def __init__(self, fobj=None):
        self.param_names = ('time', 'param1', 'param2', 'param3',
                            'param4', 'param5')
        super(Event_Wait, self).__init__(fobj)
        self.name = 'Wait'

    @property
    def time(self):
        return self.param0

    @time.setter
    def time(self, value):
        self.param0 = value


class Event_MoveLandInit(Event):
    """ Event # 13 """
    def __init__(self, fobj=None):
        self.param_names = ('target', 'param1', 'param2', 'param3',
                            'param4', 'param5')
        super(Event_MoveLandInit, self).__init__(fobj)
        self.name = 'MoveLandInit'

    @property
    def target(self):
        return self.param0

    @target.setter
    def target(self, value):
        self.param0 = value


class Event_MoveLandCmd(Event):
    """ Event # 14 """
    def __init__(self, fobj=None):
        self.param_names = ('direction', 'distance', 'speed', 'moveKind',
                            'startSE', 'endSE')
        super(Event_MoveLandCmd, self).__init__(fobj)
        self.name = 'MoveLandCmd'

    @property
    def direction(self):
        return self.param0

    @direction.setter
    def direction(self, value):
        # direction must be one of 2, 4, 6, or 8
        if value in [2, 4, 6, 8]:
            self.param0 = value
        else:
            raise ValueError

    @property
    def distance(self):
        return self.param1

    @distance.setter
    def distance(self, value):
        self.param1 = value

    @property
    def speed(self):
        return self.param2

    @speed.setter
    def speed(self, value):
        # speed must be one of 0, 1, 2, 3, or 4
        if value in [0, 1, 2, 3, 4]:
            self.param2 = value
        else:
            raise ValueError

    @property
    def moveKind(self):
        return self.param3

    @moveKind.setter
    def moveKind(self, value):
        # moveKind must be one of 0, 1, 2, 3, or 4
        if value in [0, 1, 2, 3, 4]:
            self.param3 = value
        else:
            raise ValueError

    @property
    def startSE(self):
        return self.param4

    @startSE.setter
    def startSE(self, value):
        self.param4 = value

    @property
    def endSE(self):
        return self.param5

    @endSE.setter
    def endSE(self, value):
        self.param5 = value


class Event_Flag(Event):
    """ Event # 17 """
    def __init__(self, fobj=None):
        super(Event_Flag, self).__init__(fobj)
        self.name = 'Flag'


class Event_ToFlag(Event):
    """ Event # 18 """
    def __init__(self, fobj=None):
        super(Event_ToFlag, self).__init__(fobj)
        self.name = 'ToFlag'


class Event_DamageMoveLandInit(Event):
    """ Event # 19 """
    def __init__(self, fobj=None):
        self.param_names = ('target', 'param1', 'param2', 'param3',
                            'param4', 'param5')
        super(Event_DamageMoveLandInit, self).__init__(fobj)
        self.name = 'DamageMoveLandInit'

    @property
    def target(self):
        return self.param0

    @target.setter
    def target(self, value):
        self.param0 = value
