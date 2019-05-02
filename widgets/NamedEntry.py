""" Slightly modified Entry so that it has a string in a label before it """

from tkinter import Frame, Entry, Label, StringVar


class NamedEntry(Frame):
    def __init__(self, master, name):
        self.master = master
        self.name = StringVar(value=name)
        Frame.__init__(self, self.master)

        Label(self, textvariable=self.name).grid(row=0, column=0)
        self.entry = Entry(self)
        self.entry.grid(row=0, column=1)

    def modify(self, var, *args, **kwargs):
        if kwargs.get('_name') is not None:
            self.rename(kwargs.get('_name'))
        configs = kwargs.get('configs', dict())
        configs.update({'textvariable': var})
        self.entry.config(**configs)

    def rename(self, name):
        self.name.set(name)
