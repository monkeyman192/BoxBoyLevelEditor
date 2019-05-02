from tkinter import Toplevel, IntVar, StringVar, Entry, Frame
from tkinter.ttk import Combobox

from widgets import WidgetTable, NamedEntry
from events import EventHandler


EVENT_KINDS = ['OnEnterScene', 'OnEnterArea', 'OnCalled', 'OnCalledDirect',
               'OnGroupDisappeared', 'CallChain', 'Wait', 'WaitWithLock',
               'LockCamera', 'UnlockCamera', 'ControlCamera', 'AppearGroup',
               'DisappearGroup', 'MoveLandInit', 'MoveLandCmd', 'ConveyorSet',
               'ConveyorOverride', 'Flag', 'ToFlag', 'DamageMoveLandInit']


class EventWindow(Toplevel):
    def __init__(self, master, event_data):
        self.master = master
        self.event_data = event_data
        Toplevel.__init__(self, self.master)
        self.withdraw()

        self._create_widgets()
        self.deiconify()

    def _create_widgets(self):
        self.frame = Frame(self)
        self.frame.grid(sticky='nsew')

        Label(self.frame, text='Select a sequence: ').grid(column=0, row=0)
        self.seq_choice = Combobox(self.frame)
        self.seq_choice.grid(column=1, row=0)

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
            add_options=EVENT_KINDS,
            adder_script=self.add_event_from_selection)
        self.event_table.grid(column=0, row=1, columnspan=2, sticky='nsew')

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def add_event_from_selection(self):
        selected_kind = self.event_table.nameselection.get()
        kind = EVENT_KINDS.index(selected_kind)
        print(kind)
        handler = EventHandler(self.event_data)
        new_event = handler.new_event(kind)
        # Iterate over the parameters. If there is a name for it, then change
        # the NamedEntry's name to that.
        for i in range(6):
            if new_event.param_names[i] != 'param{0}'.format(i):
                print(new_event.param_names[i])
            else:
                # make it so that the value can't be modified??
                print('param{0} cannot be modified'.format(i))
