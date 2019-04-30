from tkinter import (Canvas, Toplevel, Frame, Button, Checkbutton, Scrollbar,
                     Menu, Entry, Label)
from tkinter import BooleanVar, IntVar, StringVar
from tkinter import NORMAL, HIDDEN, VERTICAL, HORIZONTAL, ALL, DISABLED, RIDGE
from PIL import Image, ImageTk

from utils import check_int
from layer_data import GIMMICKS, LAYER1, LAYER6, MAP_DATA
from modify_image import apply_mods
from gimmicks.GimmickHandler import GimmickHandler
from gimmicks.Gimmicks import Gimmick_Gravity, Gimmick_Shutter, Gimmick_Laser
from SpriteHandler import get_sprite
from pushblock_handler import (pushblock_image, update_bounds,
                               update_pushblock_sprites)

BLOCK_COLOURS = {1: '#000000',
                 2: '#FF0000',
                 5: '#FF00FF',
                 8: '#FF0000'}

ACTIVEOUTLINE = '#FF5000'

"""
Tag information:
The base map data has the tag 'MAP'.
Each layer has it's own individual tag:
'LAYER0', through to 'LAYER6'
Gimmicks have two tags.
'GIMMICK', and the wuid of the gimmick itself.
This way gimmicks that have mutliple things to display all have the same tag.
"""


class MapCanvas(Toplevel):
    def __init__(self, master, stage_data=None):
        self.master = master
        Toplevel.__init__(self, self.master)

        self.stage_data = stage_data
        self.gimmick_handler = GimmickHandler(self.stage_data.gimmick_data)

        self.current_gimmick = None
        self.highlighted_ids = list()

        # assign some local variables pulled from the map data
        self.height = len(self.stage_data.map_layout)
        self.width = len(self.stage_data.map_layout[0])
        self.box_number = IntVar(value=self.stage_data.box_number)
        self.box_set_num = IntVar(value=self.stage_data.box_set_num)

        # register the entry validation function
        self._validate_check_int = self.register(check_int)
        self._validate_and_apply = self.register(
            self._validate_and_apply_param)

        # StringVar's to allow the gimmick info panel to show the correct name
        self.gimmick_type_name = StringVar(value='n/a')
        self.param0_name = StringVar(value='param0')
        self.param1_name = StringVar(value='param1')
        self.param2_name = StringVar(value='param2')
        self.param3_name = StringVar(value='param3')
        self.param4_name = StringVar(value='param4')
        self.param5_name = StringVar(value='param5')

        self.gimmick_wuid = IntVar()
        self.gimmick_group = IntVar()
        self.pushblock_group = IntVar()

        # Values for the param entries.
        # There are 2 values for each in case the value is packed like '<hh'
        self.param0_value_1 = IntVar()
        self.param0_value_2 = IntVar()
        self.param1_value_1 = IntVar()
        self.param1_value_2 = IntVar()
        self.param2_value_1 = IntVar()
        self.param2_value_2 = IntVar()
        self.param3_value_1 = IntVar()
        self.param3_value_2 = IntVar()
        self.param4_value_1 = IntVar()
        self.param4_value_2 = IntVar()
        self.param5_value_1 = IntVar()
        self.param5_value_2 = IntVar()

        self.show_gimmicks = BooleanVar(value=False)
        self.show_layer0 = BooleanVar(value=False)
        self.show_layer1 = BooleanVar(value=False)
        self.show_layer2 = BooleanVar(value=False)
        self.show_layer3 = BooleanVar(value=False)
        self.show_layer4 = BooleanVar(value=False)
        self.show_layer5 = BooleanVar(value=False)
        self.show_layer6 = BooleanVar(value=False)
        self.show_pushblocks = BooleanVar(value=False)

        # Stage data
        self.stage_data_tiles = dict()
        self.stage_layer_sprites = dict()
        # Gimmick data
        self.gimmicks = list()
        self.gimmick_sprites = dict()
        self.gimmick_data = dict()
        # Layer data
        self.layer0_tiles = list()
        self.layer1_tiles = list()
        self.layer1_sprites = dict()
        self.layer2_tiles = list()
        self.layer3_tiles = list()
        self.layer4_tiles = list()
        self.layer5_tiles = list()
        self.layer6_tiles = list()
        self.layer6_sprites = dict()

        self.pushblock_sprites = dict()
        self.pushblock_data = dict()
        self.pushblock_tiles = dict()

        self._create_widgets()

        self.popup_menu = Menu(self.canvas, tearoff=0)

        self._create_menu()

        # Add all the bindings
        self.canvas.bind('<ButtonPress-1>', self.button_press)
        self.canvas.bind('<ButtonRelease-1>', self.button_release)
        self.canvas.bind('<B1-Motion>', self.drag_block)
        self.canvas.bind('<ButtonPress-3>', self._show_popup)

        self.canvas.bind('<Left>', self.scroll_left)
        self.canvas.bind('<Right>', self.scroll_right)
        self.canvas.bind('<Up>', self.scroll_up)
        self.canvas.bind('<Down>', self.scroll_down)

        self._draw_map_data()

        self.current_selection = None
        self.moving_item = False
        self.curr_item_location = None
        self.add_item_location = None
        self.hints_shown = False

    def _add_gimmick(self, kind, **kwargs):
        # Toggle the gimmicks on First
        if not self.show_gimmicks.get():
            self.show_gimmicks.set(True)
            self._toggle_gimmicks()
        new_obj = self.gimmick_handler.new(
            kind,
            self.add_item_location[0],
            self.add_item_location[1],
            **kwargs)
        self._draw_gimmick(new_obj)

    def _add_gravity(self, direction):
        """ Add a gravity tile. """
        if not self.show_layer6.get():
            self.show_layer6.set(True)
            self._toggle_layer6()
        self._add_gimmick(27, direction=direction)

    def _add_pushblock(self, group):
        """ Add a pushblock in the specified group. """
        x = self.add_item_location[0]
        y = self.add_item_location[1]
        pushblock = self.stage_data.pushblocks[group]
        if (x, y) not in pushblock.block_locations:
            pushblock.block_locations.append((x, y))
            pushblock.num_blocks += 1
            image = pushblock_image(None, self.pushblock_sprites)
            ID = self.canvas.create_image(
                32 * x,
                32 * (self.height - y),
                image=image,
                tags='PUSHBLOCK_{0}'.format(str(group)),
                anchor='sw')
            # If the pushblock group doesn't already exist, add it.
            if group not in self.pushblock_data:
                self.pushblock_data[group] = dict()
                self.pushblock_data[group]['ids'] = [ID]
                self.pushblock_data[group]['obj'] = pushblock
            else:
                self.pushblock_data[group]['ids'].append(ID)
                # remove the old bounds image
                self.canvas.delete(self.pushblock_data[group]['bounds'])
            self.pushblock_tiles[ID] = image

            # Update the bounds of the push box
            ID = update_bounds(pushblock, self.pushblock_data[group], self)
            if self.current_selection is None:
                self.canvas.itemconfig(ID, state=HIDDEN)
            else:
                if 'PUSHBLOCK_{0}'.format(str(group)) in self.canvas.gettags(
                        self.current_selection):
                    self.canvas.itemconfig(ID, state=NORMAL)
                else:
                    self.canvas.itemconfig(ID, state=HIDDEN)

            update_pushblock_sprites(pushblock, group, self)

    def _add_terrain(self, kind):
        x = self.add_item_location[0] // 32
        y = self.add_item_location[1] // 32
        ID = self.canvas.create_rectangle(
            32 * x, 32 * y,
            32 * (x + 1), 32 * (y + 1),
            fill=BLOCK_COLOURS.get(kind, '#AAAAAA'))
        self.stage_data_tiles[ID] = (x, y)
        self.stage_data.map_layout[y][x] = kind

        # Draw the sprite automatically
        if not self.show_layer1.get():
            self.show_layer1.set(True)
            self._toggle_layer1()

        ID = self._determine_sprite_id(x, y)
        self._draw_sprite(ID, x, y)

        self.stage_data.layer1_data[y][x] = ID

        self._redraw_surrounding_sprites(x, y)

    def _validate_and_apply_param(self, new_value, how, param, comp=None):
        """ Apply the value in the entry to the gimmick.

        Parameters
        ----------
        gimmick : Gimmick
            Gimmick to apply the value to
        param : int, str (in {0, 1, 2, 3, 4, 5}, or 'wuid' or 'group')
            Param number.
        comp : int (in {0, 1}) or None
            Whether it is the first or second component.
        """
        if how == 'forced':
            # If the widget is assigned the value from the Gimmick we will
            # assume it is fine and not validate it.
            return True
        if check_int(new_value):
            if new_value == '' or new_value == '-':
                return True
            if self.current_gimmick:
                if param == 'wuid' or param == 'group':
                    setattr(self.current_gimmick, param, int(new_value))
                else:
                    # find out whether the parameter is a tuple or int
                    param = int(param)
                    if self.current_gimmick.param_fmts[param] == '<i':
                        setattr(self.current_gimmick,
                                'param{0}'.format(str(param)),
                                int(new_value))
                    if self.current_gimmick.param_fmts[param] == '<hh':
                        comp = int(comp)
                        curr_value = list(
                            getattr(self.current_gimmick,
                                    'param{0}'.format(str(param))))
                        curr_value[1 - comp] = int(new_value)
                        setattr(self.current_gimmick,
                                'param{0}'.format(str(param)),
                                tuple(curr_value))
                if isinstance(self.current_gimmick, Gimmick_Laser):
                    if param == 0:
                        # Laser direction. Redraw the image if the direction
                        # changes
                        if self.current_selection is not None:
                            self._redraw_gimmick(self.current_gimmick,
                                                 [self.current_selection])
                if isinstance(self.current_gimmick, Gimmick_Gravity):
                    # For the gravity gimmick, we want to re-draw it if the
                    # position or extent have changed...
                    if param in (0, 1):
                        if self.current_selection is not None:
                            self._redraw_gimmick(self.current_gimmick,
                                                 [self.current_selection])
            return True
        return False

    def _determine_sprite_id(self, x, y):
        local_array = [i[x-1:x+2] for i in self.stage_data.map_layout[y-1:y+2]]
        return get_sprite(local_array)

    def _draw_sprite(self, sprite_id, x, y):
        # apply a sprite automatically
        image = self._get_layer_image(sprite_id, 1)
        if image is None:
            ID = self.canvas.create_rectangle(
                32 * x, 32 * y,
                32 * (x + 1), 32 * (y + 1),
                fill='#222222', tags='LAYER1',
                activeoutline=ACTIVEOUTLINE)
        else:
            ID = self.canvas.create_image(
                32 * x, 32 * (y + 1),
                image=image, tags='LAYER1',
                anchor='sw')
        self.layer1_tiles.append(ID)

    def _draw_gimmick(self, gimmick):
        try:
            gimmick_img_data = gimmick.image(GIMMICKS)
        except KeyError:
            print('Invalid value.')
        if gimmick_img_data is None:
            # Don't draw it or anything...
            return
        image = self._get_gimmick_image(gimmick_img_data)
        if isinstance(image, list):
            for drawing_params in image:
                if 'rectangle' in drawing_params:
                    coords = drawing_params.pop('rectangle')
                    ID = self.canvas.create_rectangle(
                        coords[0], 32 * self.height - coords[1],
                        coords[2], 32 * self.height - coords[3],
                        activeoutline=ACTIVEOUTLINE,
                        tags=('GIMMICK', 'IMMOVABLE',
                              'wuid_' + str(gimmick.wuid),
                              'kind_' + str(gimmick.kind),
                              *gimmick.extra_tags),
                        **drawing_params)
                elif 'text' in drawing_params:
                    position = drawing_params.pop('position')
                    ID = self.canvas.create_text(
                        position[0] + 5,
                        32 * self.height - position[1] + 5,
                        tags=('GIMMICK', 'TEXT',
                              'wuid_' + str(gimmick.wuid),
                              'kind_' + str(gimmick.kind),
                              *gimmick.extra_tags),
                        **drawing_params,
                        anchor='nw')
                elif 'image' in drawing_params:
                    image = self._get_gimmick_image(
                        drawing_params['image'])
                    position = drawing_params['position']
                    ID = self.canvas.create_image(
                        position[0],
                        32 * self.height - position[1] + 32,
                        image=image,
                        tags=('GIMMICK',
                              'wuid_' + str(gimmick.wuid),
                              'kind_' + str(gimmick.kind),
                              *gimmick.extra_tags),
                        anchor='sw')
                self.gimmicks.append(ID)
                self.gimmick_data[ID] = gimmick

        else:
            ID = self.canvas.create_image(
                gimmick.x,
                32 * self.height - gimmick.y + 32,
                image=image,
                tags=('GIMMICK', 'wuid_' + str(gimmick.wuid),
                      'kind_' + str(gimmick.kind),
                      *gimmick.extra_tags),
                anchor='sw')
            self.gimmicks.append(ID)
            self.gimmick_data[ID] = gimmick
        # Horizontal shutters have another part rotated and placed
        # across from them
        if isinstance(gimmick, Gimmick_Shutter):
            # first, find the location of the other shutter
            if gimmick.direction == 1:
                left_coord = int(self.canvas.coords(ID)[1])
                right_side_ids = self.canvas.find_withtag(
                    'SHUTTER_R')
                closest_x = float('inf')
                for ID in right_side_ids:
                    x, y = self.canvas.coords(ID)
                    if int(y) == left_coord:
                        if x < closest_x:
                            closest_x = int(x)
                if closest_x == float('inf'):
                    # If nothing is found just move on
                    return
                # now we should have the x and y location
                img_data = {'path': gimmick_img_data['path'],
                            'mods': ['rot_270']}
                image = self._get_gimmick_image(img_data)
                ID = self.canvas.create_image(
                    closest_x, left_coord,
                    image=image,
                    tags=('GIMMICK',
                          'wuid_' + str(gimmick.wuid),
                          'kind_' + str(gimmick.kind),
                          *gimmick.extra_tags),
                    anchor='sw')
                self.gimmicks.append(ID)
                self.gimmick_data[ID] = gimmick

    def _redraw_gimmick(self, gimmick, old_IDs):
        """ Redraw the specified gimmick """
        for ID in old_IDs:
            self.canvas.delete(ID)
            del self.gimmick_data[ID]
        self._draw_gimmick(gimmick)
        self.current_selection = self.gimmicks[-1]

    def _redraw_surrounding_sprites(self, x, y):
        for loc in [(x - 1, y), (x + 1, y), (x, y + 1), (x, y - 1)]:
            a, b = loc[0], loc[1]
            ID = self._determine_sprite_id(a, b)
            if ID is None:
                continue
            if (ID != self.stage_data.layer1_data[b][a] and
                    self.stage_data.layer1_data[b][a] != -1):
                # remove the old sprite
                old_id = self.canvas.find_closest(32 * a + 1, 32 * b + 1)[0]
                if old_id in self.layer1_tiles:
                    self.canvas.delete(old_id)
                    self.layer1_tiles.remove(old_id)
                # draw the new sprite
                self._draw_sprite(ID, a, b)
                self.stage_data.layer1_data[b][a] = ID

    def _assign_number_to_layer(self):
        print('Sorry, not implemented yet...')

    def _toggle_hint_gimmicks(self):
        # get a list of all the ID's relating to HINT objects
        hint_ids = self.canvas.find_withtag('HINT')
        if self.hints_shown:
            for ID in hint_ids:
                self.canvas.itemconfig(ID, state=HIDDEN)
            self.hints_shown = False
        else:
            for ID in hint_ids:
                self.canvas.itemconfig(ID, state=NORMAL)
            self.hints_shown = True

    def _create_widgets(self):
        map_frame = Frame(self)
        map_frame.grid(column=0, row=0, sticky='nsew', rowspan=3)
        self.canvas = Canvas(map_frame, height='10c', width='15c')
        self.canvas.grid(column=0, row=0, sticky='nsew')
        xsb = Scrollbar(map_frame, orient=HORIZONTAL)
        ysb = Scrollbar(map_frame, orient=VERTICAL)
        xsb.config(command=self.canvas.xview)
        ysb.config(command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=xsb.set)
        self.canvas.configure(yscrollcommand=ysb.set)
        xsb.grid(column=0, row=1, sticky='ew')
        ysb.grid(column=1, row=0, sticky='ns')

        info_frame = Frame(self)
        info_frame.grid(column=1, row=0, sticky='ew')

        # Info frame to modify map properties

        map_info_frame = Frame(info_frame, relief=RIDGE, bd=2)
        map_info_frame.grid(column=0, row=0, sticky='ew')

        Label(map_info_frame, text='Number of boxes:').grid(column=0, row=0,
                                                            sticky='w')
        Entry(
            map_info_frame,
            width=3,
            validate=ALL,
            validatecommand=(self._validate_check_int, '%P',
                             [1, 2, 3, 4, 5, 6, 7, 8, 9]),
            textvariable=self.box_number).grid(row=0, column=1, sticky='w')
        Label(map_info_frame, text='Box groups:').grid(column=0, row=1,
                                                       sticky='w')
        Entry(
            map_info_frame,
            width=3,
            validate=ALL,
            validatecommand=(self._validate_check_int, '%P', [1, 2]),
            textvariable=self.box_set_num).grid(row=1, column=1, sticky='w')

        # Frame to edit properties of the currently selected gimmick

        gimmick_edit_frame = Frame(info_frame, relief=RIDGE, bd=2)
        gimmick_edit_frame.grid(column=0, row=1, sticky='ew')

        Label(gimmick_edit_frame, textvariable=self.gimmick_type_name).grid(
            column=0, row=0, sticky='w', columnspan=3)

        Label(gimmick_edit_frame,
              text='wuid').grid(column=0, row=1, sticky='w')
        Entry(gimmick_edit_frame, width=5, validate=ALL,
              validatecommand=(self._validate_and_apply, '%P', '%V', 'wuid'),
              textvariable=self.gimmick_wuid).grid(column=1, row=1, sticky='w')
        Label(gimmick_edit_frame,
              text='group').grid(column=0, row=2, sticky='w')
        Entry(gimmick_edit_frame, width=5, validate=ALL,
              validatecommand=(self._validate_and_apply, '%P', '%V', 'group'),
              textvariable=self.gimmick_group).grid(column=1, row=2,
                                                    sticky='w')

        Label(gimmick_edit_frame,
              textvariable=self.param0_name).grid(column=0, row=3)
        self.param0_entry1 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 0, 0),
                                   textvariable=self.param0_value_1)
        self.param0_entry1.grid(column=1, row=3)
        self.param0_entry2 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 0, 1),
                                   textvariable=self.param0_value_2)
        self.param0_entry2.grid(column=2, row=3)
        Label(gimmick_edit_frame,
              textvariable=self.param1_name).grid(column=0, row=4)
        self.param1_entry1 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 1, 0),
                                   textvariable=self.param1_value_1)
        self.param1_entry1.grid(column=1, row=4)
        self.param1_entry2 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 1, 1),
                                   textvariable=self.param1_value_2)
        self.param1_entry2.grid(column=2, row=4)
        Label(gimmick_edit_frame,
              textvariable=self.param2_name).grid(column=0, row=5)
        self.param2_entry1 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 2, 0),
                                   textvariable=self.param2_value_1)
        self.param2_entry1.grid(column=1, row=5)
        self.param2_entry2 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 2, 1),
                                   textvariable=self.param2_value_2)
        self.param2_entry2.grid(column=2, row=5)
        Label(gimmick_edit_frame,
              textvariable=self.param3_name).grid(column=0, row=6)
        self.param3_entry1 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 3, 0),
                                   textvariable=self.param3_value_1)
        self.param3_entry1.grid(column=1, row=6)
        self.param3_entry2 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 3, 1),
                                   textvariable=self.param3_value_2)
        self.param3_entry2.grid(column=2, row=6)
        Label(gimmick_edit_frame,
              textvariable=self.param4_name).grid(column=0, row=7)
        self.param4_entry1 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 4, 0),
                                   textvariable=self.param4_value_1)
        self.param4_entry1.grid(column=1, row=7)
        self.param4_entry2 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 4, 1),
                                   textvariable=self.param4_value_2)
        self.param4_entry2.grid(column=2, row=7)
        Label(gimmick_edit_frame,
              textvariable=self.param5_name).grid(column=0, row=8)
        self.param5_entry1 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 5, 0),
                                   textvariable=self.param5_value_1)
        self.param5_entry1.grid(column=1, row=8)
        self.param5_entry2 = Entry(gimmick_edit_frame, width=5, validate=ALL,
                                   validatecommand=(self._validate_and_apply,
                                                    '%P', '%V', 5, 1),
                                   textvariable=self.param5_value_2)
        self.param5_entry2.grid(column=2, row=8)

        # Frame to modify pushblock info

        pushblock_frame = Frame(info_frame, relief=RIDGE, bd=2)
        pushblock_frame.grid(column=0, row=2, sticky='ew')

        Label(pushblock_frame, text='Pushbox Info').grid(column=0, row=0,
                                                         columnspan=2)
        Label(pushblock_frame, text='Group:').grid(column=0, row=1)
        Entry(pushblock_frame,
              textvariable=self.pushblock_group,
              validate=ALL,
              width=5,
              state=DISABLED,
              validatecommand=(self._validate_check_int, '%P')).grid(column=1,
                                                                     row=1)

        # Frame to toggle the visible layers

        toggle_frame = Frame(info_frame, relief=RIDGE, bd=2)
        toggle_frame.grid(column=0, row=3, sticky='ew')

        Checkbutton(toggle_frame,
                    text='Show Gimmicks',
                    variable=self.show_gimmicks,
                    command=self._toggle_gimmicks).grid(column=0, row=0,
                                                        sticky='w',
                                                        columnspan=2)
        Checkbutton(toggle_frame,
                    text='Show Layer 0',
                    variable=self.show_layer0).grid(column=0, row=1,
                                                    sticky='w', columnspan=2)
        Checkbutton(toggle_frame,
                    text='Show Layer 1',
                    variable=self.show_layer1,
                    command=self._toggle_layer1).grid(column=0, row=2,
                                                      sticky='w', columnspan=2)
        Checkbutton(toggle_frame,
                    text='Show Layer 2',
                    variable=self.show_layer2).grid(column=0, row=3,
                                                    sticky='w', columnspan=2)
        Checkbutton(toggle_frame,
                    text='Show Layer 3',
                    variable=self.show_layer3).grid(column=0, row=4,
                                                    sticky='w', columnspan=2)
        Checkbutton(toggle_frame,
                    text='Show Layer 4',
                    variable=self.show_layer4).grid(column=0, row=5,
                                                    sticky='w', columnspan=2)
        Checkbutton(toggle_frame,
                    text='Show Layer 5',
                    variable=self.show_layer5).grid(column=0, row=6,
                                                    sticky='w', columnspan=2)
        Checkbutton(toggle_frame,
                    text='Show Layer 6',
                    variable=self.show_layer6,
                    command=self._toggle_layer6).grid(column=0, row=7,
                                                      sticky='w', columnspan=2)

        Checkbutton(toggle_frame,
                    text='Show Pushblocks',
                    variable=self.show_pushblocks,
                    command=self._toggle_pushblocks).grid(column=0, row=8,
                                                          sticky='w',
                                                          columnspan=2)

        # TODO: move
        Button(toggle_frame, text='Export', command=self._export_map).grid(
            column=0, row=9)

        # get map to expand fully
        map_frame.grid_columnconfigure(index=0, weight=1)
        map_frame.grid_rowconfigure(index=0, weight=1)
        self.columnconfigure(index=0, weight=1)
        self.rowconfigure(index=0, weight=1)

    def _create_menu(self):
        # Add gimmicks cascade
        self.gimmick_menu = Menu(self.popup_menu, tearoff=0)
        self.popup_menu.add_cascade(label='Add Gimmick',
                                    menu=self.gimmick_menu)
        self.gimmick_menu.add_command(
            label='Laser',
            command=lambda: self._add_gimmick(3))
        # Add terrain cascade
        self.terrain_menu = Menu(self.popup_menu, tearoff=0)
        self.popup_menu.add_cascade(label='Add Terrain',
                                    menu=self.terrain_menu)
        self.terrain_menu.add_command(
            label='Ground',
            command=lambda: self._add_terrain(1))
        self.terrain_menu.add_command(
            label='Upward spikes',
            command=lambda: self._add_terrain(2))
        self.terrain_menu.add_command(
            label='Downward spikes',
            command=lambda: self._add_terrain(8))
        self.terrain_menu.add_command(
            label='Sticky block',
            command=lambda: self._add_terrain(51))
        # Add gravity cascade
        self.gravity_menu = Menu(self.popup_menu, tearoff=0)
        self.popup_menu.add_cascade(label='Add Gravity',
                                    menu=self.gravity_menu)
        self.gravity_menu.add_command(label='Up',
                                      command=lambda: self._add_gravity(0))
        self.gravity_menu.add_command(label='Down',
                                      command=lambda: self._add_gravity(1))
        self.gravity_menu.add_command(label='Left',
                                      command=lambda: self._add_gravity(2))
        self.gravity_menu.add_command(label='Right',
                                      command=lambda: self._add_gravity(3))
        # Add pushblock cascade
        self.pushblock_menu = Menu(self.popup_menu, tearoff=0)
        self.popup_menu.add_cascade(label='Add Pushblock',
                                    menu=self.pushblock_menu)
        for i in range(8):
            self.pushblock_menu.add_command(
                label='Group {0}'.format(i),
                command=lambda i=i: self._add_pushblock(i))
        # Add menu to allow for specifying a specific value in any layer
        self.popup_menu.add_command(
            label='Assign number',
            command=self._assign_number_to_layer)
        self.popup_menu.add_command(
            label='Toggle hint visibility',
            command=self._toggle_hint_gimmicks)

    def _draw_map_data(self):
        for y, row in enumerate(self.stage_data.map_layout):
            for x, i in enumerate(row):
                if i != 0:
                    if i in MAP_DATA:
                        image = self._get_layer_image(i, 'map')
                        ID = self.canvas.create_image(
                            32 * x, 32 * (y + 1),
                            image=image, tags='MAP', anchor='sw')
                    else:
                        ID = self.canvas.create_rectangle(
                            32 * x, 32 * y,
                            32 * (x + 1), 32 * (y + 1),
                            fill=BLOCK_COLOURS.get(i, '#AAAAAA'),
                            tags='MAP', activeoutline=ACTIVEOUTLINE)
                    self.stage_data_tiles[ID] = (x, y)
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))

    def _export_map(self):
        # Assign any modified data then save the map
        self.stage_data.box_number = self.box_number.get()
        self.stage_data.box_set_num = self.box_set_num.get()

        self.stage_data.save()

    def _show_popup(self, event):
        self.add_item_location = (
            32 * int(self.canvas.canvasx(event.x) // 32),
            32 * (self.height - int(self.canvas.canvasy(event.y) // 32)))
        self.popup_menu.post(event.x_root, event.y_root)

    def _show_gimmick_info(self, gimmick):
        """ Display the relevant info relating to the selected gimmick """
        self.gimmick_wuid.set(gimmick.wuid)
        self.gimmick_group.set(gimmick.group)
        self.gimmick_type_name.set(gimmick.name)
        for i, name in enumerate(gimmick.param_names):
            name_var = getattr(self, 'param{0}_name'.format(str(i)))
            name_var.set(name)
            param_value1 = getattr(self, 'param{0}_value_1'.format(str(i)))
            param_value2 = getattr(self, 'param{0}_value_2'.format(str(i)))
            param_entry2 = getattr(self, 'param{0}_entry2'.format(str(i)))
            if gimmick.param_fmts[i] == '<i':
                param_value1.set(getattr(gimmick, 'param{0}'.format(str(i))))
                param_value2.set(0)
                param_entry2.config(state=DISABLED)
            elif gimmick.param_fmts[i] == '<hh':
                # display the params in the opposite order as they are flipped
                param_value1.set(getattr(gimmick,
                                         'param{0}'.format(str(i)))[1])
                param_value2.set(getattr(gimmick,
                                         'param{0}'.format(str(i)))[0])
                param_entry2.config(state=NORMAL)
        if hasattr(gimmick, 'target_id'):
            # If the object has a target_id attribute we want to highlight it
            # for easy visibility
            target_id = gimmick.target_id
            if target_id == -1:
                # Highlight the toggle blocks
                self._highlight_obj(7, iskind=True)
            else:
                # Highlight whatever it is meant to be targeting
                self._highlight_obj(target_id)

    def _toggle_gimmicks(self):
        # TODO: have gimmicks always appear on top
        if self.show_gimmicks.get() is True:
            if len(self.gimmicks) != 0:
                for ID in self.gimmicks:
                    self.canvas.itemconfig(ID, state=NORMAL)
            else:
                for gimmick in self.gimmick_handler.gimmicks:
                    self._draw_gimmick(gimmick)
            self.hints_shown = True
        else:
            for ID in self.gimmicks:
                self.canvas.itemconfig(ID, state=HIDDEN)
            self.hints_shown = False

    def _get_gimmick_image(self, gimmick_img_data):
        if 'drawn' in gimmick_img_data:
            return gimmick_img_data['drawn']
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

    def _get_layer_image(self, ID, layer):
        layer_map = {'map': MAP_DATA, 1: LAYER1, 6: LAYER6}
        if layer == 'map':
            sprite_layer = self.stage_layer_sprites
        else:
            sprite_layer = getattr(self, 'layer{0}_sprites'.format(str(layer)))
        if ID in sprite_layer:
            image = sprite_layer[ID]
        else:
            img_data = layer_map[layer].get(ID)
            if img_data is not None:
                img = Image.open(img_data['path'])
                img = apply_mods(img, img_data.get('mods'))
                sprite_layer[ID] = ImageTk.PhotoImage(img)
                image = sprite_layer[ID]
            else:
                image = None
        return image

    def _highlight_obj(self, _id, iskind=False):
        # un-highlight any currently highlighted objects
        for ID in self.highlighted_ids:
            self.canvas.delete(ID)
        if iskind:
            _id = 'kind_' + str(_id)
        else:
            _id = 'wuid_' + str(_id)
        # Then highlight everything that needs to be
        self.highlighted_ids = list()
        for ID in self.canvas.find_withtag(_id):
            x, y, = self.canvas.coords(ID)
            temp_ID = self.canvas.create_rectangle(
                x, y, x + 32, y - 32,
                fill='', width=3, outline='#FF0000')
            self.highlighted_ids.append(temp_ID)

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
                        image = self._get_layer_image(i, 1)

                        extra_tags = tuple()
                        if i == 66:
                            # We give the right side of the shutter sprite
                            # an extra tag to make it easy to find later.
                            extra_tags = ('SHUTTER_R',)

                        if image is None:
                            ID = self.canvas.create_rectangle(
                                32 * x, 32 * y,
                                32 * (x + 1), 32 * (y + 1),
                                fill='#000000', tags=('LAYER1', *extra_tags),
                                activeoutline=ACTIVEOUTLINE)
                        else:
                            ID = self.canvas.create_image(
                                32 * x, 32 * (y + 1),
                                image=image, tags=('LAYER1', *extra_tags),
                                anchor='sw')
                        self.layer1_tiles.append(ID)
            for ID in self.stage_data_tiles:
                self.canvas.itemconfig(ID, state=HIDDEN)
        else:
            for ID in self.layer1_tiles:
                self.canvas.itemconfig(ID, state=HIDDEN)
            for ID in self.stage_data_tiles:
                self.canvas.itemconfig(ID, state=NORMAL)

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
                            image = self._get_layer_image(i, 6)
                            ID = self.canvas.create_image(
                                32 * x, 32 * (y + 1),
                                image=image, tags='LAYER6',
                                anchor='sw')
                            self.layer6_tiles.append(ID)
        else:
            for ID in self.layer6_tiles:
                self.canvas.itemconfig(ID, state=HIDDEN)

    def _toggle_pushblocks(self):
        # Toggle the visibility of pushblocks
        if self.show_pushblocks.get() is True:
            if len(self.pushblock_data) != 0:
                for pb_data in self.pushblock_data.values():
                    for ID in pb_data['ids']:
                        self.canvas.itemconfig(ID, state=NORMAL)
            else:
                for num, block in enumerate(self.stage_data.pushblocks):
                    if block.num_blocks != 0:
                        self.pushblock_data[num] = {'obj': block,
                                                    'ids': list(),
                                                    'bounds': None}
                        pb_imgs = pushblock_image(
                            block, self.pushblock_sprites)
                        for i in range(block.num_blocks):
                            image = pb_imgs[i]
                            ID = self.canvas.create_image(
                                32 * block.block_locations[i][0],
                                32 * (self.height -
                                      block.block_locations[i][1]),
                                image=image,
                                tags='PUSHBLOCK_{0}'.format(str(i)),
                                anchor='sw')
                            self.pushblock_data[num]['ids'].append(ID)
                            self.pushblock_tiles[ID] = image
                        # Also create the bounds rectangle and hide it by
                        # default
                        ID = update_bounds(block, self.pushblock_data[num],
                                           self)
                        self.canvas.itemconfig(ID, state=HIDDEN)
        else:
            for pb_data in self.pushblock_data.values():
                for ID in pb_data['ids']:
                    self.canvas.itemconfig(ID, state=HIDDEN)
                self.canvas.itemconfig(pb_data['bounds'], state=HIDDEN)

    def button_press(self, event):
        self.canvas.focus_set()  # keybinds don't work without this

        self.current_selection = self.canvas.find_withtag("current")

        if len(self.current_selection) == 0:
            return None
        self.current_selection = self.current_selection[0]

        self.curr_item_location = self.canvas.coords(self.current_selection)

        # If we have selected a gimmick, show its information
        if self.current_selection in self.gimmicks:
            self.current_gimmick = self.gimmick_data[self.current_selection]
            self._show_gimmick_info(self.current_gimmick)

        # If we have selected a moavble block, show its bounds
        if self.current_selection in self.pushblock_tiles.keys():
            # find which movable block it belongs to
            for i, pb_data in self.pushblock_data.items():
                if self.current_selection in pb_data['ids']:
                    self.canvas.itemconfig(pb_data['bounds'], state=NORMAL)
                    self.pushblock_group.set(i)
                else:
                    self.canvas.itemconfig(pb_data['bounds'], state=HIDDEN)
        else:
            self.pushblock_group.set(0)

    def button_release(self, event):
        """ Un-assign the current selection and apply any modifications to
        the moved object. """
        if not self.moving_item:
            self.curr_item_location = None
            return
        if self.current_selection in self.gimmicks:
            gimmick = self.gimmick_data[self.current_selection]
            gimmick.x = int(self.curr_item_location[0])
            gimmick.y = 32 * self.height - int(self.curr_item_location[1]) + 32
        # redraw the sprites in the push block if needed
        if self.current_selection in self.pushblock_tiles.keys():
            pb_group = self.pushblock_group.get()
            pushblock_data = self.pushblock_data[pb_group]
            pushblock = pushblock_data['obj']
            # Check if the pushblock has actually changed position.
            # If it has, check if any boxes need to be redrawn.
            # We only need to actually redraw the sprites which have changed.
            loc = pushblock_data['ids'].index(self.current_selection)
            new_position = (
                int(self.curr_item_location[0] // 32),
                self.height - int(self.curr_item_location[1] // 32))
            if new_position != pushblock.block_locations[loc]:
                pushblock.block_locations[loc] = new_position
                update_pushblock_sprites(pushblock, pb_group, self)
                # Update the bounds
                old_ID = self.pushblock_data[pb_group]['bounds']
                ID = update_bounds(pushblock, self.pushblock_data[pb_group],
                                   self)
                self.canvas.delete(old_ID)
                self.canvas.itemconfig(ID, state=NORMAL)
        # reset the current selection to be None
        self.current_selection = None
        self.curr_item_location = None

    def drag_block(self, event):
        if self.current_selection is None:
            return
        if (self.current_selection in self.layer1_tiles or
                self.current_selection in self.stage_data_tiles or
                self.current_selection in self.pushblock_tiles.keys()):
            x = 32 * (self.canvas.canvasx(event.x) // 32)
            y = 32 * (self.canvas.canvasy(event.y) // 32)
        else:
            x = 16 * (self.canvas.canvasx(event.x) // 16)
            y = 16 * (self.canvas.canvasy(event.y) // 16)
        if ((x, y) != self.curr_item_location and
                'IMMOVABLE' not in self.canvas.gettags(
                    self.current_selection)):
            self.moving_item = True
            if self.canvas.type(self.current_selection) == 'image':
                self.canvas.coords(self.current_selection, [x, y])
            else:
                self.canvas.coords(self.current_selection, [x, y,
                                                            x + 32, y + 32])
            self.curr_item_location = (x, y)

    def scroll_left(self, event):
        self.canvas.xview_moveto(self.canvas.xview()[0] - 1 / self.width)

    def scroll_right(self, event):
        self.canvas.xview_moveto(self.canvas.xview()[0] + 1 / self.width)

    def scroll_up(self, event):
        self.canvas.yview_moveto(self.canvas.yview()[0] - 1 / self.height)

    def scroll_down(self, event):
        self.canvas.yview_moveto(self.canvas.yview()[0] + 1 / self.height)
