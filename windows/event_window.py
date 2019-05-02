from tkinter import IntVar, StringVar, DISABLED, NORMAL
from tkinter import Button, Entry, Frame, Label, Toplevel
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

        if len(self.event_data) == 0:
            self.curr_seq_displayed = StringVar(value='None')
        else:
            self.curr_seq_displayed = StringVar(value='0')

        self._create_widgets()
        self.deiconify()

    def _create_widgets(self):
        self.frame = Frame(self)
        self.frame.grid(sticky='nsew')

        Label(self.frame, text='Select a sequence: ').grid(column=0, row=0,
                                                           sticky='w')
        if len(self.event_data) == 0:
            seq_choices = ['None']
        else:
            seq_choices = list(range(len(self.event_data)))

        self.seq_choice = Combobox(self.frame,
                                   textvariable=self.curr_seq_displayed,
                                   values=seq_choices,
                                   state='readonly')
        self.seq_choice.bind("<<ComboboxSelected>>",
                             self.change_displayed_seq)
        self.seq_choice.grid(column=1, row=0, sticky='w')

        Button(self.frame, text='Add', command=self._event_seq_add).grid(
            column=2, row=0, sticky='w')
        Button(self.frame, text='Remove', command=self._event_seq_remove).grid(
            column=3, row=0, sticky='w')
        Button(self.frame, text='Save', command=self._event_seq_save).grid(
            column=4, row=0, sticky='w')

        self.event_table = WidgetTable(
            self.frame,
            headings=['wuid', 'kind', 'param0', 'param1', 'param2', 'param3',
                      'param4', 'param5'],
            pattern=[IntVar, StringVar,
                     {'var': IntVar, '_name': 'Unused_0'},
                     {'var': IntVar, '_name': 'Unused_1'},
                     {'var': IntVar, '_name': 'Unused_2'},
                     {'var': IntVar, '_name': 'Unused_3'},
                     {'var': IntVar, '_name': 'Unused_4'},
                     {'var': IntVar, '_name': 'Unused_5'}],
            widgets_pattern=[Entry, Entry,
                             lambda x: NamedEntry(x, 'Unused_0'),
                             lambda x: NamedEntry(x, 'Unused_1'),
                             lambda x: NamedEntry(x, 'Unused_2'),
                             lambda x: NamedEntry(x, 'Unused_3'),
                             lambda x: NamedEntry(x, 'Unused_4'),
                             lambda x: NamedEntry(x, 'Unused_5')],
            add_options=EVENT_KINDS,
            adder_script=self.add_event_from_selection)
        self.event_table.grid(column=0, row=1, columnspan=5, sticky='nsew')

        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _event_seq_add(self):
        """ Add a new event sequence. """
        pass

    def _event_seq_remove(self):
        """ Remove the currently selected event sequence. """
        pass

    def _event_seq_save(self):
        """ Save the currently selected event sequence. """
        event_data = self.event_table.get()
        curr_sel = int(self.curr_seq_displayed.get())
        for i in range(len(event_data)):
            event_data[i][1] = EVENT_KINDS.index(event_data[i][1])
            event = self.event_data[curr_sel].event_data[i]
            event.wuid = int(event_data[i][0])
            event.kind = int(event_data[i][1])
            for j in range(6):
                pname = 'param{0}'.format(str(j))
                setattr(event, pname, int(event_data[i][j + 2]))

    def _extract_event_data(self, event):
        # Iterate over the parameters. If there is a name for it, then change
        # the NamedEntry's name to that.
        data = list()
        data.append(event.wuid)
        data.append(EVENT_KINDS[event.kind])
        for i in range(6):
            param_name = event.param_names[i]
            pname = 'param{0}'.format(i)
            if param_name != pname:
                data.append({'var': getattr(event, pname),
                             '_name': param_name,
                             'configs': {'state': NORMAL}})
            else:
                # make it so that the value can't be modified??
                data.append({'var': 0, 'configs': {'state': DISABLED}})
        return data

    def add_event_from_selection(self):
        selected_kind = self.event_table.nameselection.get()
        kind = EVENT_KINDS.index(selected_kind)
        handler = EventHandler(self.event_data)
        new_event = handler.new_event(kind)
        return self._extract_event_data(new_event)

    def change_displayed_seq(self, event):
        choice = self.seq_choice.get()
        if choice == 'None':
            return
        # TODO: add a popup to inform the user that the event sequence must be
        # saved before changing
        choice = int(choice)
        seq_data = self.event_data[choice]
        data = list()
        for event in seq_data.event_data:
            data.append(self._extract_event_data(event))
        self.event_table.set(data)
