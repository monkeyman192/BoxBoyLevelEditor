""" Slightly modified Entry so that it has a string in a label before it """

from tkinter import Frame, Entry, Label


class NamedEntry(Frame):
    def __init__(self, master, name):
        self.master = master
        Frame.__init__(self, self.master)

        Label(self, text=name).grid(row=0, column=0)
        self.entry = Entry(self)
        self.entry.grid(row=0, column=1)

    def modify(self, var, *args, **kwargs):
        self.entry.config(textvariable=var)
