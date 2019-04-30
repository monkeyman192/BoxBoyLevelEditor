from tkinter import Toplevel, IntVar, StringVar, Entry, Frame

from widgets import WidgetTable, NamedEntry


class EventWindow(Toplevel):
    def __init__(self, master, data=None):
        self.master = master
        self.data = data
        Toplevel.__init__(self, self.master)
        self.withdraw()

        self._create_widgets()
        self.deiconify()

    def _create_widgets(self):
        self.frame = Frame(self)
        self.frame.grid(sticky='nsew')

        self.event_table = WidgetTable(
            self.frame,
            headings=['wuid', 'kind', 'param0', 'param1', 'param2', 'param3',
                      'param4', 'param5'],
            pattern=[IntVar, StringVar, IntVar, IntVar, IntVar, IntVar,
                     IntVar, IntVar],
            widgets_pattern=[Entry, Entry,
                             lambda x: NamedEntry(x, 'p0'),
                             lambda x: NamedEntry(x, 'p1'),
                             lambda x: NamedEntry(x, 'p2'),
                             lambda x: NamedEntry(x, 'p3'),
                             lambda x: NamedEntry(x, 'p4'),
                             lambda x: NamedEntry(x, 'p5')],
            add_options=['OnEnterScene', 'OnEnterArea', 'OnCalled',
                         'OnCalledDirect', 'OnGroupDisappeared', 'Wait',
                         'WaitWithLock', 'LockCamera', 'UnlockCamera',
                         'ControlCamera', 'AppearGroup', 'DisappearGroup',
                         'MoveLandInit', 'MoveLandCmd', 'ConveyorSet',
                         'ConveyorOverride', 'Flag', 'ToFlag',
                         'DamageMoveLandInit'],
            adder_script=self.add_event_from_selection)
        self.event_table.grid(sticky='nsew')

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def add_event_from_selection(self):
        selected_kind = self.event_table.nameselection.get()
        print(selected_kind)
