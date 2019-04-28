import struct
import os.path as op
from lxml import etree


LAYER_NAMES = {0: 'unknown',
               1: 'sprites',
               2: 'lines',
               3: 'shading',
               4: 'hints_1',
               5: 'hints_2',
               6: 'gravity_tracks'}


def extract_map_data(fname):
    with open(fname, 'rb') as f:
        # First, read the stage layout info
        f.seek(0x20)
        # find offset
        offset = struct.unpack('<I', f.read(0x4))[0]
        # go to offset
        f.seek(offset)
        width, height, area, offset = struct.unpack('<IIII', f.read(0x10))
        f.seek(offset)
        data = list()
        for y in range(height):
            data.append(list())
            for x in range(width):
                data[y].append(struct.unpack('<I', f.read(0x4))[0])
        with open(op.join(op.dirname(fname), 'map_data.csv'), 'w') as f_out:
            for line in data[::-1]:
                f_out.write(','.join([str(l) for l in line]) + '\n')
        # next read the 7 layers of info
        for i in range(7):
            data = list()
            f.seek(0x94 + i * 0x4)
            offset = struct.unpack('<I', f.read(0x4))[0]
            f.seek(offset)
            _, offset = struct.unpack('<II', f.read(0x8))
            f.seek(offset)
            for y in range(height):
                data.append(list())
                for x in range(width):
                    data[y].append(struct.unpack('<i', f.read(0x4))[0])
            with open(op.join(op.dirname(fname),
                              'layer_{0}_{1}.csv'.format(str(i),
                                                         LAYER_NAMES[i])),
                      'w') as f_out:
                for line in data[::-1]:
                    f_out.write(','.join([str(l) for l in line]) + '\n')
        # next is the gimmick data:
        # write this to an xml file
        root = etree.Element('Gimmicks')
        f.seek(0xB0)
        offset = struct.unpack('<I', f.read(0x4))[0]
        f.seek(offset)
        count = struct.unpack('<I', f.read(0x4))[0]
        for i in range(count):
            gimmick_data = etree.Element('Gimmick_{0}'.format(str(i)))
            wuid = etree.Element('wuid')
            wuid.text = str(struct.unpack('<i', f.read(0x4))[0])  # 0x00
            gimmick_data.append(wuid)
            kind = etree.Element('kind')
            kind.text = str(struct.unpack('<i', f.read(0x4))[0])  # 0x04
            gimmick_data.append(kind)
            x = etree.Element('x')
            x.text = str(struct.unpack('<i', f.read(0x4))[0]//32)  # 0x08
            gimmick_data.append(x)
            y = etree.Element('y')
            y.text = str(struct.unpack('<i', f.read(0x4))[0]//32)  # 0x0C
            gimmick_data.append(y)
            group = etree.Element('group')
            group.text = str(struct.unpack('<i', f.read(0x4))[0])  # 0x10
            gimmick_data.append(group)
            appearance = etree.Element('appearance')
            appearance.text = str(struct.unpack('<i', f.read(0x4))[0])  # 0x14
            gimmick_data.append(appearance)
            param0 = etree.Element('param0')
            param0.text = str(struct.unpack('<hh', f.read(0x4))[::-1])  # 0x18
            gimmick_data.append(param0)
            param1 = etree.Element('param1')
            param1.text = str(struct.unpack('<hh', f.read(0x4))[::-1])  # 0x1C
            gimmick_data.append(param1)
            param2 = etree.Element('param2')
            param2.text = str(struct.unpack('<hh', f.read(0x4))[::-1])  # 0x20
            gimmick_data.append(param2)
            param3 = etree.Element('param3')
            param3.text = str(struct.unpack('<hh', f.read(0x4))[::-1])  # 0x24
            gimmick_data.append(param3)
            param4 = etree.Element('param4')
            param4.text = str(struct.unpack('<hh', f.read(0x4))[::-1])  # 0x28
            gimmick_data.append(param4)
            param5 = etree.Element('param5')
            param5.text = str(struct.unpack('<hh', f.read(0x4))[::-1])  # 0x2C
            gimmick_data.append(param5)
            root.append(gimmick_data)
        with open(op.join(op.dirname(fname), 'gimmicks.xml'), 'w') as f_out:
            f_out.write(etree.tostring(root, encoding=str, pretty_print=True))


""" NOTES:

what each layer is:
data_map:
 0 - empty
 1 - ground
 2 - upward spikes
 5 - Special (see other layer???)
 7 - Mystery block (star blocks)
 8 - downward spikes
16 - 21 - moving blocks
28 - left conveyor - slow
29 - right conveyor - slow
30 - left conveyor - medium
31 - right conveyor - medium
32 - left conveyor - fast (?)
33 - right conveyor - fast (?)
36 - left spike conveyor - slow (?)
37 - right spike conveyor - slow
38 - left spike conveyor - medium
39 - right spike conveyor - medium
40 - left spike conveyor - fast
41 - right spike conveyor - fast
51 - sticky block
52 - 57 - moving electro blocks. Each number block moves in the same way

layer 0: ???

layer 1: map tile sprite
# TODO: come up with better names...
 0 - convex NW
 2 - convex NE
 3 - convex NE & NW
 4 - convex NW & SW
 5 - also normal??
 6 - convex NE & SE
 8 - normal
11 - convex SW
13 - convex SE
14 - convex SE & SW
15 - convex NE & NW & SW & SE
18 - concave NE & NW
19 - concave SE
20 - concave SW
22 - concave NE & NW
24 - concave NE
25 - concave NW
# sticky walls
41 - sticky-wall N & W
42 - sticky-wall N
43 - sticky-wall N & E
44 - sticky-wall W & N & E
45 - sticky-wall S & W & N
46 - sticky-wall S & N
47 - sticky-wall S & E & N
48 - sticky-wall W
49 - Normal wall
50 - sticky-wall E
51 - sticky-wall E & W
52 - sticky-wall S & W
53 - sticky-wall S
54 - sticky-wall S & E
55 - sticky-wall S & E & W
56 - sticky-wall N & S & E & W
# half-width pieces
57 - Top half, left end
58 - Top half
59 - Top half, right end
60 - Left half, top end
61 - Right half, top end
62 - Bottom half, left end
63 - Bottom half
64 - Bottom half, right end
65 - Left half
66 - Right half
67 - Left half, bottom end
68 - Right half, bottom end
69 - Top half, left and right end
70 - Bottom half, left and right end
71 - Left half, top and bottom end
72 - Right half, top and bottom end
# More sticky walls, with grey corners for thin pieces.
73 - Sticky-wall N & W, SE grey
74 - Sticky-wall N & E, SW grey
75 - Sticky-wall S & W, NE grey
76 - Sticky-wall S & E, NW grey
77 - Sticky-wall S, NE & NW grey
78 - Sticky-wall E, SW & NW grey
79 - Sticky-wall W, NE & SE grey
80 - Sticky-wall N, SE & SW grey
100 - Past Boy (greyed out "dead" (?) Qbby)
300 - up-facing spikes individual
301 - up-facing spikes
302 - up-facing spikes left end
303 - up-facing spikes right end
304 - moving blocks
317 - down-facing spike individual (?)
318 - down-facing spikes
319 - down-facing spikes left end
320 - down-facing spikes right end

layer 2: crane lines?
28 - crane end circle
31 - horizontal crane line
34 - vertical crane line
37 - horizontal crane line - top half
40 - horizontal crane line - bottom half
57 - ??? dot?
63 - ??? dot bottom half with line?
68 - top crane line end
69 - left crane line end
70 - left crane line end - top half
71 - left crane line end - bottom half
74 - right crane line end - top half
75 - right crane line end - bottom half
78 - bottom crane line end
79 - right crane line end
81 - vertical double closed-ended line
86 - double vertical line top
89 - double vertical line bottom
90 - SE corner lines with dot
91 - SW corner lines with dot
92 - NE corner lines with dot
93 - NW corner lines with dot

layer 3: background shading?
# This is used to give an area the dark fading at the bottom by having 55's
# until a layer of 54's (eg. see 8-6)
54 - light shading
55 - dark shading?

layer 4 & 5: Hints
 0 - Qbby (facing right?)
 1 - white box - raised
 2 - Qbby attached to box facing right (no legs)
 3 - Qbby extruding box facing right
 4 - white box
 5 - grey box
 6 - Qbby facing left
 7 - Qbby legs?
 8 - ?
 9 - Qbby extruding box facing left
10 - moving block
12 - Raised dummy block NW
13 - Raised dummy block N
14 - Raised dummy block NE
16 - Raised dummy block NEW
17 - Raised dummy block center
19 - Raised dummy block W
21 - Raised dummy block E
24 - Raised dummy block SW
26 - Raised dummy block SE
28 - Dummy block NW
29 - Dummy block N
30 - Dummy block NE
31 - Dummy block EW
33 - Dummy block W
35 - Dummy block center
37 - Dummy block E
39 - Dummy block SW
40 - Dummy block S
41 - Dummy block SE
42 - Dummy block NS
94 - down-facing crane top point
95 - crane vertical line
96 - down-facing crane arm
97 - grey box in air??
110 - left-facing crane top point
112 - left-facing crane arm
114 - white boxes in air
115 - Qbby attached to boxes facing right
117 - right-facing crane top point
118 - right-facing crane arm
120 - white boxes in air
121 - Qbby attached to boxes facing right
123 - '1' Icon
124 - '2' Icon

layer 6: Gravity fields
-1 - Nothing
 1 - up-moving gravity a
 2 - up-moving gravity b
 3 - left-moving gravity a
 4 - right-moving gravity a
 5 - left-moving gravity b
 6 - right-moving gravity b
 7 - down-moving gravity a
 8 - down-moving gravity b

Gimmick data:
 - General:
    x and y values are divided by 32 to get the square they lie on.
kind:
 0 - Spawn point
  param0 : respawn point number
  param1 : 0 if initial, 1 is quick-respawn
  param2 : always 1
  Still not sure about the following other than initial x position...
  param3 : (initial x position of region, width of region)
   For the inital spawn point this is just the position of the start point
  param4 : (initial y position of region, height of region) ???
   (0, 0) for the initial start point
  param5 : always (-1, -1)
 1 - Next stage door (for time attack)
  param1: stage to go to
 2 - World exit door
 from Archive.bin: category, step, enterID
  param0 : If 1 leave world?
  param1 : if 1 leave map?
 3 - Laser (located 1 block higher than it looks like it should be)
  param0 :
   2 - Facing down
   4 - Facing left
   6 - Facing right
   8 - Facing up
 4 - Crown (located 1 block higher than it looks like it should be)
  All params always 0?
 5 - InitCamera
 6 - Button (located 1 block higher than it looks like it should be)
  param0:
   2 - Facing down
   4 - Facing left
   6 - Facing right
   8 - Facing up
  param1 : always 1? (possibly 0 = OneTime, 1 = Toggle)
  param2 : wuid of the door to open, or -1 to toggle the toggle blocks
 7 - Toggle blocks (located 1 block higher than it looks like it should be)
  param0:
   0 - starts off
   1 - starts on
 8 - Break block
 9 - Something to do with a fixed camera position
10 - StartDoor
11 - Shutter
 param0 : direction : 0: vertical, 1: horizontal
 param1 : already open : 0: No, 1: Yes
12 - Priority Camera
13 - Hint Area
 param0/param1: an area? (mRect)
 param2/param3: another area? (mPlayerRect)
14 - Assist Block
15 - "Guide Board" (Help image I think?)
 param0: help image id?
16 - Chellenge String
17 - Falling spikes
 param0: direction (?) Always 2...
 param1: fall rate (?)
18 - Spikey
 param0: x, y : override position?
 param1: x, y : whether to use the override position??
19 - Score dot (for Score attack)
20 - Fall Block Controller
21 - Medal Guide
22 - Battery (Plus/Minus blocks)
 param0: (enum) 0: 'Plus', 1: 'Minus'
 param1: (bool) Is a toggle (ie. 0 means it is only a single use...)
 param2: (int) TargetId. -1 for a toggle for (-) blocks, and 0 for (+) blocks
23 - Warp Cloud
 group: used to link which one you fall down through
 param0: 0 if facing up, 1 if facing down
 param1: (start x cordinate, start y coordinate)
 param2: (width, height)
 param3: For up-facing smoke, this is the number of the group to spit you
  out of. For down facing it is just 0.
24 - Crane end joint
 group: used to link start and end points and crane
 param0: 0 if start, 1 if end
25 - Crane
 group: use to link to end joints
 param0: crane direction:
  0 : down
  1 : left
  2 : right
 param1: max pole length.
 param2: Move type:
  0 : Separate
  1 : Round (Return to start)
  2 : Stop (Stop at end point)
 param3: (possibly used? not sure... If so values are):
  0 : Wait
  1 : Lengthen
  2 : Shorten
  3 : ShortenOver
  4 : ShortenForce
  5 : Catch
  6 : CatchWait
  7 : NotCatchWait
  8 : Release
  9 : ReleaseForce
  10: ReleaseWait
  11: Move
  12: CloseToOpen
26 - Spikey end point (located 1 block higher than it looks like it should be)
 param0: wuid of raising door to activate
27 - Gravity field
 param0: <hh position
 param1: <hh extent
 param2: (bool) Is active
 param3: Direction:
  0 : Up
  1 : Down
  2 : Left
  3 : Right
 param4: Speed
  0 : Lv1
  1 : Lv2
  2 : Lv3
  3 : Lv4
28 - World entry door
 param0: world id
29 - Shop entry door
30 - EndingDoor
31 - Dark Cloud
32 - Projector
33 - World Switch
34 - Dark Cloud Boss
35 - Chest
 group: indicates contents I guess?
36 - Dark Cloud Last
37 - Door Last Monument
38 - World Transporter
39 - Hako Big Land
40 - Box Planet
41 - World Arrow
"""
