from tkinter import (Canvas, Toplevel, Frame, Button, Checkbutton, Scrollbar,
                     Menu)
from tkinter import BooleanVar
from tkinter import NORMAL, HIDDEN, VERTICAL, HORIZONTAL, ALL
from PIL import Image, ImageTk

from layer_data import GIMMICKS, LAYER1
from modify_image import apply_mods
from GimmickHandler import GimmickHandler

BLOCK_COLOURS = {1: '#000000',
                 2: '#FF0000',
                 5: '#FF00FF'}


class MapCanvas(Toplevel):
    def __init__(self, master, stage_data=None):
        self.master = master
        Toplevel.__init__(self, self.master)

        self.stage_data = stage_data
        self.gimmick_handler = GimmickHandler(self.stage_data.gimmick_data)

        self.height = len(self.stage_data.map_layout)
        self.width = len(self.stage_data.map_layout[0])

        self.show_gimmicks = BooleanVar(value=False)
        self.show_layer0 = BooleanVar(value=False)
        self.show_layer1 = BooleanVar(value=False)
        self.show_layer2 = BooleanVar(value=False)
        self.show_layer3 = BooleanVar(value=False)
        self.show_layer4 = BooleanVar(value=False)
        self.show_layer5 = BooleanVar(value=False)
        self.show_layer6 = BooleanVar(value=False)

        self.stage_data_tiles = list()
        self.gimmicks = list()
        self.gimmick_sprites = dict()
        self.gimmick_map = dict()
        self.layer0_tiles = list()
        self.layer1_tiles = list()
        self.layer1_sprites = dict()
        self.layer2_tiles = list()
        self.layer3_tiles = list()
        self.layer4_tiles = list()
        self.layer5_tiles = list()
        self.layer6_tiles = list()

        self._create_widgets()

        self.popup_menu = Menu(self.canvas, tearoff=0)

        self._create_menu()

        # Add all the bindings
        self.canvas.bind('<ButtonPress-1>', self.button_press)
        self.canvas.bind('<ButtonRelease-1>', self.button_release)
        self.canvas.bind('<B1-Motion>', self.drag_block)
        self.canvas.bind('<ButtonPress-3>', self._show_popup)

        self._draw_map_data()

        self.current_selection = None
        self.curr_item_location = None
        self.add_item_location = None

    def _add_gimmick(self, kind):
        # Toggle the gimmicks on First
        self.show_gimmicks.set(True)
        self._toggle_gimmicks()
        new_obj = self.gimmick_handler.new(
            kind,
            self.add_item_location[0],
            self.add_item_location[1])
        gimmick_img_data = new_obj.image(GIMMICKS)
        image = self._get_gimmick_image(gimmick_img_data)
        ID = self.canvas.create_image(
            new_obj.x,
            new_obj.y,
            image=image,
            anchor='sw')
        self.gimmicks.append(ID)
        self.gimmick_map[ID] = new_obj
        self.canvas.itemconfig(ID, state=NORMAL)

    def _create_widgets(self):
        self.canvas = Canvas(self)
        self.canvas.grid(column=0, row=0, sticky='nsew')
        xsb = Scrollbar(self, orient=HORIZONTAL)
        ysb = Scrollbar(self, orient=VERTICAL)
        xsb.config(command=self.canvas.xview)
        ysb.config(command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=xsb.set)
        self.canvas.configure(yscrollcommand=ysb.set)
        xsb.grid(column=0, row=1, sticky='ew')
        ysb.grid(column=1, row=0, sticky='ns')
        edit_frame = Frame(self)
        edit_frame.grid(column=2, row=0)
        Button(edit_frame, text='hi').grid(column=0, row=0)
        Checkbutton(edit_frame,
                    text='Show Gimmicks',
                    variable=self.show_gimmicks,
                    command=self._toggle_gimmicks).grid(column=0, row=1,
                                                        sticky='w')
        Checkbutton(edit_frame,
                    text='Show Layer 0',
                    variable=self.show_layer0).grid(column=0, row=2,
                                                    sticky='w')
        Checkbutton(edit_frame,
                    text='Show Layer 1',
                    variable=self.show_layer1,
                    command=self._toggle_layer1).grid(column=0, row=3,
                                                      sticky='w')
        Checkbutton(edit_frame,
                    text='Show Layer 2',
                    variable=self.show_layer2).grid(column=0, row=4,
                                                    sticky='w')
        Checkbutton(edit_frame,
                    text='Show Layer 3',
                    variable=self.show_layer3).grid(column=0, row=5,
                                                    sticky='w')
        Checkbutton(edit_frame,
                    text='Show Layer 4',
                    variable=self.show_layer4).grid(column=0, row=6,
                                                    sticky='w')
        Checkbutton(edit_frame,
                    text='Show Layer 5',
                    variable=self.show_layer5).grid(column=0, row=7,
                                                    sticky='w')
        Checkbutton(edit_frame,
                    text='Show Layer 6',
                    variable=self.show_layer6,
                    command=self._toggle_layer6).grid(column=0, row=8,
                                                      sticky='w')

        Button(edit_frame, text='Export', command=self._export_map).grid(
            column=0, row=9)

        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)

    def _create_menu(self):
        self.gimmick_menu = Menu(self.popup_menu, tearoff=0)
        self.popup_menu.add_cascade(label='Add Gimmick',
                                    menu=self.gimmick_menu)
        self.gimmick_menu.add_command(
            label='Laser',
            command=lambda: self._add_gimmick(3))
        self.gimmick_menu.add_command(
            label='Crown',
            command=lambda: self._add_gimmick(4))

    def _draw_map_data(self):
        for y, row in enumerate(self.stage_data.map_layout):
            for x, i in enumerate(row):
                if i != 0:
                    ID = self.canvas.create_rectangle(
                        32 * x, 32 * y,
                        32 * (x + 1), 32 * (y + 1),
                        fill=BLOCK_COLOURS.get(i, '#AAAAAA'))
                    self.stage_data_tiles.append(ID)
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

    def _export_map(self):
        with open('step01.bin', 'wb') as f:
            f.write(bytes(self.stage_data))

    def _show_popup(self, event):
        self.add_item_location = (self.canvas.canvasx(event.x),
                                  self.canvas.canvasy(event.y))
        self.popup_menu.post(event.x_root, event.y_root)

    def _toggle_gimmicks(self):
        if self.show_gimmicks.get() is True:
            if len(self.gimmicks) != 0:
                for ID in self.gimmicks:
                    self.canvas.itemconfig(ID, state=NORMAL)
            else:
                for gimmick in self.gimmick_handler.gimmicks:
                    gimmick_img_data = gimmick.image(GIMMICKS)
                    if gimmick_img_data is None:
                        # Don't draw it or anything...
                        continue
                    image = self._get_gimmick_image(gimmick_img_data)
                    ID = self.canvas.create_image(
                        gimmick.x,
                        32 * self.height - gimmick.y + 32,
                        image=image,
                        anchor='sw')
                    self.gimmicks.append(ID)
                    self.gimmick_map[ID] = gimmick
        else:
            for ID in self.gimmicks:
                self.canvas.itemconfig(ID, state=HIDDEN)

    def _get_gimmick_image(self, gimmick_img_data):
        sprite_name = '{0}_{1}'.format(
            gimmick_img_data['path'],
            gimmick_img_data.get('mods', ''))
        if sprite_name in self.gimmick_sprites:
            image = self.gimmick_sprites[sprite_name]
        else:
            img = Image.open(gimmick_img_data['path'])
            img = apply_mods(img, gimmick_img_data.get('mods'))
            self.gimmick_sprites[sprite_name] = ImageTk.PhotoImage(
                img)
            image = self.gimmick_sprites[sprite_name]
        return image

    def _draw_layer0(self):
        # Unknown
        pass

    def _toggle_layer1(self):
        # Sprites
        if self.show_layer1.get() is True:
            if len(self.layer1_tiles) != 0:
                # if there is already data just un-hide it
                for ID in self.layer1_tiles:
                    self.canvas.itemconfig(ID, state=NORMAL)
            else:
                # otherwise draw the tiles
                for y, row in enumerate(self.stage_data.layer1_data):
                    for x, i in enumerate(row):
                        if i == -1:
                            continue
                        if i in self.layer1_sprites:
                            image = self.layer1_sprites[i]
                        else:
                            img_data = LAYER1.get(i)
                            if img_data is not None:
                                img = Image.open(img_data['path'])
                                img = apply_mods(img, img_data.get('mods'))
                                self.layer1_sprites[i] = ImageTk.PhotoImage(
                                    img)
                                image = self.layer1_sprites[i]
                            else:
                                image = None

                        if image is None:
                            ID = self.canvas.create_rectangle(
                                32 * x, 32 * y,
                                32 * (x + 1), 32 * (y + 1),
                                fill='#222222')
                        else:
                            ID = self.canvas.create_image(
                                32 * x, 32 * (y + 1),
                                image=image,
                                anchor='sw')
                        self.layer1_tiles.append(ID)
        else:
            for ID in self.layer1_tiles:
                self.canvas.itemconfig(ID, state=HIDDEN)

    def _draw_layer2(self):
        # Lines
        pass

    def _draw_layer3(self):
        # Shading
        pass

    def _draw_layer4(self):
        # Hints 1
        pass

    def _draw_layer5(self):
        # Hints 2
        pass

    def _toggle_layer6(self):
        # Gravity tracks
        if self.show_layer6.get() is True:
            if len(self.layer6_tiles) != 0:
                # if there is already data just un-hide it
                for ID in self.layer6_tiles:
                    self.canvas.itemconfig(ID, state=NORMAL)
            else:
                # otherwise draw the tiles
                for y, row in enumerate(self.stage_data.layer6_data):
                    for x, i in enumerate(row):
                        if i != -1:
                            ID = self.canvas.create_rectangle(
                                32 * x, 32 * y,
                                32 * (x + 1), 32 * (y + 1),
                                fill='#222222')
                            self.layer6_tiles.append(ID)
        else:
            for ID in self.layer6_tiles:
                self.canvas.itemconfig(ID, state=HIDDEN)

    def button_press(self, event):
        canvas = event.widget
        self.current_selection = canvas.find_withtag("current")[0]

    def button_release(self, event):
        """ Un-assign the current selection and apply any modifications to
        the moved object. """
        if self.current_selection in self.gimmicks:
            gimmick = self.gimmick_map[self.current_selection]
            gimmick.x = int(self.curr_item_location[0])
            gimmick.y = 32 * self.height - int(self.curr_item_location[1]) + 32
        # reset the current selection to be None
        self.current_selection = None

    def drag_block(self, event):
        if self.current_selection is not None:
            if (self.current_selection in self.layer1_tiles or
                    self.current_selection in self.stage_data_tiles):
                x = 32 * (self.canvas.canvasx(event.x) // 32)
                y = 32 * (self.canvas.canvasy(event.y) // 32)
            else:
                x = 16 * (self.canvas.canvasx(event.x) // 16)
                y = 16 * (self.canvas.canvasy(event.y) // 16)
            if self.canvas.type(self.current_selection) == 'image':
                self.canvas.coords(self.current_selection, [x, y])
            else:
                self.canvas.coords(self.current_selection, [x, y,
                                                            x + 32, y + 32])
            self.curr_item_location = (x, y)
