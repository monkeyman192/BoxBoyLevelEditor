from tkinter import Tk, Frame, Button, filedialog, Label, BOTH
import os
import os.path as op
import shutil

from FileTreeview import FileTreeview
from Settings import Settings
from serialization.mappack import unpack_map, pack_map
from map_formats.read_map import extract_map_data
from MapCanvas import MapCanvas
from map_formats.bbmap import BBMap


class MapEditor(Frame):
    def __init__(self, master):
        self.master = master
        Frame.__init__(self, self.master)

        self.master.protocol("WM_DELETE_WINDOW", self._check_exit)
        self.master.title("BoxBoyEditor")

        settings_path = os.path.join(os.getenv('APPDATA'), 'BBEdit')

        self.settings = Settings(op.join(settings_path, 'settings.json'))

        self.paths = dict()
        if (self.settings.read('ROMFS_PATCH') is None or
                self.settings.read('ROMFS_ORIG') is None):
            self._get_paths()
        else:
            self.paths['ROMFS_ORIG'] = self.settings.read('ROMFS_ORIG')
            self.paths['ROMFS_PATCH'] = self.settings.read('ROMFS_PATCH')

        # ensure that the romfs path is the actual romfs folder.
        romfs_patch = self.paths['ROMFS_PATCH']
        if romfs_patch is not None:
            if op.basename(romfs_patch).lower() != 'romfs':
                self.paths['ROMFS_PATCH'] = op.join(romfs_patch, 'romfs')
                if not op.exists(self.paths['ROMFS_PATCH']):
                    os.mkdir(self.paths['ROMFS_PATCH'])
        self._create_widgets()

        # populate the file trees
        self.src_tv.generate('', self.paths['ROMFS_ORIG'])
        self.src_tv.index()
        self.dst_tv.generate('', self.paths['ROMFS_PATCH'])
        self.dst_tv.index()

        # Add all the bindings
        self.dst_tv.bind('<Return>', self.edit)
        self.src_tv.bind('<Return>', self.decompile)
        self.dst_tv.bind('<Tab>', self.tab_switch_src)
        self.src_tv.bind('<Tab>', self.tab_switch_dst)

        self.dst_tv.bind('<Control-r>', self.recompile)
        self.dst_tv.bind('<Control-s>', self.save)

        # select the first element in each tree by default for keyboard controls to work on startup
        self.src_tv.focus("I001")
        self.src_tv.selection_set("I001")
        self.src_tv.focus_set()
        self.dst_tv.focus("I001")
        self.dst_tv.selection_set("I001")

# region private functions

    def _check_exit(self):
        self.settings.write(self.paths)
        self.master.destroy()

    def _edit_map(self):
        selected = self.dst_tv.selection()
        if len(selected) == 1:
            fname = self.dst_tv.get_filepath(selected[0])
            map_data = BBMap(fname)
            MapCanvas(self, map_data)

    def _extract(self):
        for sid in self.dst_tv.selection():
            dst_fpath = self.dst_tv.get_filepath(sid)
            included_files = list()
            if op.isdir(dst_fpath):
                for directory, folders, files in os.walk(dst_fpath):
                    for fname in files:
                        if op.splitext(fname)[1] == '.bin':
                            included_files.append(op.join(directory, fname))
            else:
                included_files = [dst_fpath]
            for fpath in included_files:
                extract_map_data(fpath)

    def _decompile(self):
        for sid in self.src_tv.selection():
            src_fpath = self.src_tv.get_filepath(sid)
            included_files = list()
            if op.isdir(src_fpath):
                for directory, folders, files in os.walk(src_fpath):
                    for fname in files:
                        if op.splitext(fname)[1] == '.cmp':
                            included_files.append(op.join(directory, fname))
            else:
                if op.splitext(src_fpath)[1] == '.cmp':
                    included_files.append(src_fpath)
                else:
                    raise TypeError("File selected is not a .cmp file.")
            for fname in included_files:
                rel_path = op.relpath(op.dirname(fname),
                                      self.paths['ROMFS_ORIG'])
                # convert
                converted_fpath = unpack_map(fname)
                dst_fpath = op.join(self.paths['ROMFS_PATCH'],
                                    rel_path,
                                    op.basename(converted_fpath))
                # move
                if not op.exists(op.dirname(dst_fpath)):
                    os.makedirs(op.dirname(dst_fpath))
                shutil.move(converted_fpath, dst_fpath)
        self.dst_tv.refresh()

    def _recompile(self):
        for sid in self.dst_tv.selection():
            # TODO: make work...
            pack_map(self.dst_tv.get_filepath(sid))

    def _save(self):
        selection = op.relpath(self.dst_tv.get_filepath(self.dst_tv.selection()), self.paths['ROMFS_PATCH'])
        packed_dir = op.dirname(selection)
        patch_archive = op.join(self.paths['ROMFS_PATCH'], packed_dir, "Archive2.bin.cmp")
        rom_archive = op.join(self.paths['ROMFS_ORIG'],  packed_dir, "Archive.bin.cmp")

        if not op.exists(patch_archive):
            patch_archive = op.join(self.paths['ROMFS_PATCH'], selection, "Archive2.bin.cmp")

        shutil.copy(patch_archive, rom_archive)

    def _create_widgets(self):
        mainframe = Frame(self)
        mainframe.grid(row=0, column=0, sticky='nsew')
        Label(mainframe, text='Source').grid(row=0, column=0, sticky='ew')
        Label(mainframe, text='Patch').grid(row=0, column=1, sticky='ew')
        Label(mainframe, text='Info').grid(row=0, column=2, sticky='ew')
        src_tv_frame = Frame(mainframe)
        src_tv_frame.grid(row=1, column=0, sticky='nsew')
        self.src_tv = FileTreeview(src_tv_frame, self.paths['ROMFS_ORIG'],
                                   columns=["dtype", "filepath"],
                                   selectmode='extended',
                                   displaycolumns=["dtype"])
        self.src_tv.enhance(scrollbars=['y', 'x'],
                            sortable=True,
                            leftclick=self._select_src_entry,
                            rightclick=self._right_click_src_entry)
        self.src_tv.heading("#0", text="Directory Structure")
        self.src_tv.heading("dtype", text="Type")
        self.src_tv.column("dtype", width=50, minwidth=35, stretch=False)
        self.src_tv.pack(expand=True, fill=BOTH)

        dst_tv_frame = Frame(mainframe)
        dst_tv_frame.grid(row=1, column=1, sticky='nsew')
        self.dst_tv = FileTreeview(dst_tv_frame, self.paths['ROMFS_PATCH'],
                                   columns=["dtype", "filepath"],
                                   selectmode='extended',
                                   displaycolumns=["dtype"])
        self.dst_tv.enhance(scrollbars=['y', 'x'],
                            sortable=True,
                            leftclick=self._select_dst_entry,
                            rightclick=self._right_click_dst_entry)
        self.dst_tv.heading("#0", text="Directory Structure")
        self.dst_tv.heading("dtype", text="Type")
        self.dst_tv.column("dtype", width=50, minwidth=35, stretch=False)
        self.dst_tv.pack(expand=True, fill=BOTH)

        # bottom frame
        bottom_frame = Frame(mainframe)
        bottom_frame.grid(column=0, row=2, columnspan=3)

        Button(bottom_frame, text='Exit', command=self.master.destroy).grid(
            column=0, row=0)
        Button(bottom_frame, text='Decompile', command=self._decompile).grid(
            column=1, row=0)
        Button(bottom_frame, text='Recompile', command=self._recompile).grid(
            column=2, row=0)
        Button(bottom_frame, text='Extract', command=self._extract).grid(
            column=3, row=0)
        Button(bottom_frame, text='Edit', command=self._edit_map).grid(
            column=4, row=0)

        mainframe.grid_rowconfigure(index=0, weight=0)
        mainframe.grid_rowconfigure(index=1, weight=1)
        mainframe.grid_rowconfigure(index=2, weight=0)
        mainframe.grid_columnconfigure(index=0, weight=1)
        mainframe.grid_columnconfigure(index=1, weight=1)
        mainframe.grid_columnconfigure(index=2, weight=0)

        self.grid(column=0, row=0, sticky='nsew')

        self.grid_rowconfigure(index=0, weight=1)
        self.grid_columnconfigure(index=0, weight=1)

        self.master.grid_rowconfigure(index=0, weight=1)
        self.master.grid_columnconfigure(index=0, weight=1)

    def _select_src_entry(self, *args):
        pass

    def _right_click_src_entry(self, *args):
        pass

    def _select_dst_entry(self, *args):
        pass

    def _right_click_dst_entry(self, *args):
        pass

    def _get_paths(self):
        self.paths['ROMFS_ORIG'] = filedialog.askdirectory(
            title="Select the unpacked romfs directory")
        self.paths['ROMFS_PATCH'] = filedialog.askdirectory(
            title="Select a directory to place the patch.")
        self.settings.write(self.paths)

    # region public functions

    def decompile(self, event):
        self._decompile()

    def edit(self, event):
        self._edit_map()

    def recompile(self, event):
        self._recompile()

    def save(self, event):
        self._save()

    def tab_switch_dst(self, event):
        self.dst_tv.focus_set()
        return 'break'

    def tab_switch_src(self, event):
        self.src_tv.focus_set()
        return 'break'



if __name__ == '__main__':
    root = Tk()
    app = MapEditor(master=root)
    app.mainloop()
