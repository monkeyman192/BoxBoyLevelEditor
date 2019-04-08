MAP_DATA = {
    7: {'path': 'images\\Sprites\\07_PuzzleBlock.png'}
}
# TODO: Add the rectangles to this also to make it all in one place...


GIMMICKS = {
    0: {'path': 'images\\Gimmicks\\00_Spawn.png'},
    2: {'path': 'images\\Gimmicks\\02_Door.png'},
    3: {2: {'path': 'images\\Gimmicks\\03_Laser.png', 'mods': ['rot_90']},
        4: {'path': 'images\\Gimmicks\\03_Laser.png'},
        6: {'path': 'images\\Gimmicks\\03_Laser.png', 'mods': ['rot_180']},
        8: {'path': 'images\\Gimmicks\\03_Laser.png', 'mods': ['rot_270']}},
    4: {'path': 'images\\Gimmicks\\04_Crown.png'},
    6: {2: {'path': 'images\\Gimmicks\\06_Button.png', 'mods': ['rot_180']},
        4: {'path': 'images\\Gimmicks\\06_Button.png', 'mods': ['rot_90']},
        6: {'path': 'images\\Gimmicks\\06_Button.png', 'mods': ['rot_270']},
        8: {'path': 'images\\Gimmicks\\06_Button.png'}},
    7: {0: {'path': 'images\\Gimmicks\\07_ToggleBlock_Inactive.png'},
        1: {'path': 'images\\Gimmicks\\07_ToggleBlock_Active.png'}},
    8: {'path': 'images\\Gimmicks\\08_BreakBlock.png'},
    11: {0: {'path': 'images\\Gimmicks\\11_Shutter.png'},
         1: {'path': 'images\\Gimmicks\\11_Shutter.png', 'mods': ['rot_90']}},
    17: {'path': 'images\\Gimmicks\\17_FallSplinter.png'},
    22: {0: {'path': 'images\\Gimmicks\\22_Battery_Plus.png'},
         1: {'path': 'images\\Gimmicks\\22_Battery_Minus.png'}},
    23: {0: {'path': 'images\\Gimmicks\\23_WarpCloud.png'},
         1: {'path': 'images\\Gimmicks\\23_WarpCloud.png',
             'mods': ['rot_180']}},
    27: {0: {0: {'path': 'images\\Gimmicks\\27_0.png'},
             1: {'path': 'images\\Gimmicks\\27_0.png', 'mods': ['rot_180']},
             2: {'path': 'images\\Gimmicks\\27_0.png', 'mods': ['rot_90']},
             3: {'path': 'images\\Gimmicks\\27_0.png', 'mods': ['rot_270']}},
         1: {0: {'path': 'images\\Gimmicks\\27_1.png'},
             1: {'path': 'images\\Gimmicks\\27_1.png', 'mods': ['rot_180']},
             2: {'path': 'images\\Gimmicks\\27_1.png', 'mods': ['rot_90']},
             3: {'path': 'images\\Gimmicks\\27_1.png', 'mods': ['rot_270']}},
         2: {0: {'path': 'images\\Gimmicks\\27_2.png'},
             1: {'path': 'images\\Gimmicks\\27_2.png', 'mods': ['rot_180']},
             2: {'path': 'images\\Gimmicks\\27_2.png', 'mods': ['rot_90']},
             3: {'path': 'images\\Gimmicks\\27_2.png', 'mods': ['rot_270']}},
         3: {0: {'path': 'images\\Gimmicks\\27_3.png'},
             1: {'path': 'images\\Gimmicks\\27_3.png', 'mods': ['rot_180']},
             2: {'path': 'images\\Gimmicks\\27_3.png', 'mods': ['rot_90']},
             3: {'path': 'images\\Gimmicks\\27_3.png', 'mods': ['rot_270']}}}
}

# All the push blocks have their own images because eh... why not...
PUSHBLOCKS = {
    0: {'path': 'images\\Pushblocks\\0.png'},
    1: {'path': 'images\\Pushblocks\\1.png'},
    2: {'path': 'images\\Pushblocks\\2.png'},
    3: {'path': 'images\\Pushblocks\\3.png'},
    4: {'path': 'images\\Pushblocks\\4.png'},
    5: {'path': 'images\\Pushblocks\\5.png'},
    6: {'path': 'images\\Pushblocks\\6.png'},
    7: {'path': 'images\\Pushblocks\\7.png'},
    8: {'path': 'images\\Pushblocks\\8.png'},
    9: {'path': 'images\\Pushblocks\\9.png'},
    10: {'path': 'images\\Pushblocks\\10.png'},
    11: {'path': 'images\\Pushblocks\\11.png'},
    12: {'path': 'images\\Pushblocks\\12.png'},
    13: {'path': 'images\\Pushblocks\\13.png'},
    14: {'path': 'images\\Pushblocks\\14.png'},
    15: {'path': 'images\\Pushblocks\\15.png'},
}

LAYER1 = {
    # Sticky walls
    41: {'path': 'images\\Sprites\\43.png', 'mods': ['rot_90']},
    42: {'path': 'images\\Sprites\\42.png'},
    43: {'path': 'images\\Sprites\\43.png'},
    44: {'path': 'images\\Sprites\\55.png', 'mods': ['rot_180']},
    45: {'path': 'images\\Sprites\\55.png', 'mods': ['rot_270']},
    46: {'path': 'images\\Sprites\\46.png'},
    47: {'path': 'images\\Sprites\\55.png', 'mods': ['rot_90']},
    48: {'path': 'images\\Sprites\\42.png', 'mods': ['rot_90']},
    50: {'path': 'images\\Sprites\\42.png', 'mods': ['rot_270']},
    51: {'path': 'images\\Sprites\\46.png', 'mods': ['rot_90']},
    52: {'path': 'images\\Sprites\\43.png', 'mods': ['rot_180']},
    53: {'path': 'images\\Sprites\\42.png', 'mods': ['rot_180']},
    54: {'path': 'images\\Sprites\\43.png', 'mods': ['rot_270']},
    55: {'path': 'images\\Sprites\\55.png'},
    56: {'path': 'images\\Sprites\\56.png'},
    # Half blocks
    58: {'path': 'images\\Sprites\\58.png'},
    63: {'path': 'images\\Sprites\\58.png', 'mods': ['rot_180']},
    65: {'path': 'images\\Sprites\\58.png', 'mods': ['rot_90']},
    66: {'path': 'images\\Sprites\\58.png', 'mods': ['rot_270']},
    # More sticky walls
    73: {'path': 'images\\Sprites\\73.png'},
    74: {'path': 'images\\Sprites\\73.png', 'mods': ['rot_270']},
    75: {'path': 'images\\Sprites\\73.png', 'mods': ['rot_90']},
    76: {'path': 'images\\Sprites\\73.png', 'mods': ['rot_180']},
    77: {'path': 'images\\Sprites\\77.png'},
    78: {'path': 'images\\Sprites\\77.png', 'mods': ['rot_90']},
    79: {'path': 'images\\Sprites\\77.png', 'mods': ['rot_270']},
    80: {'path': 'images\\Sprites\\77.png', 'mods': ['rot_180']},
    # Greyed out Qbby
    100: {'path': 'images\\Sprites\\100.png'},
    # Spikes
    300: {'path': 'images\\Sprites\\300.png'},
    301: {'path': 'images\\Sprites\\301.png'},
    302: {'path': 'images\\Sprites\\302.png'},
    303: {'path': 'images\\Sprites\\303.png'},
    304: {'path': 'images\\Sprites\\304.png'},
    317: {'path': 'images\\Sprites\\300.png', 'mods': ['rot_180']},
    318: {'path': 'images\\Sprites\\301.png', 'mods': ['rot_180']},
    319: {'path': 'images\\Sprites\\303.png', 'mods': ['flip_x', 'flip_y']},
    320: {'path': 'images\\Sprites\\302.png', 'mods': ['flip_x', 'flip_y']},
}

LAYER6 = {
    1: {'path': 'images\\Gravity\\1.png'},
    2: {'path': 'images\\Gravity\\2.png'},
    3: {'path': 'images\\Gravity\\1.png', 'mods': ['rot_90']},
    4: {'path': 'images\\Gravity\\1.png', 'mods': ['rot_270']},
    5: {'path': 'images\\Gravity\\2.png', 'mods': ['rot_90']},
    6: {'path': 'images\\Gravity\\2.png', 'mods': ['rot_270']},
    7: {'path': 'images\\Gravity\\1.png', 'mods': ['rot_180']},
    8: {'path': 'images\\Gravity\\2.png', 'mods': ['rot_180']},
}
