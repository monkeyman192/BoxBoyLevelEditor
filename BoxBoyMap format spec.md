## Header:

Total size: 0x20 bytes

| Location | Datatype |           Name |
| :------- | :------: | -------------: |
| + 0x00   |  int32   |          Magic |
| + 0x04   |  int32   |        Version |
| + 0x08   |  int32   |       Filesize |
| + 0x0C   |  int32   |        Unknown |
| + 0x10   |  int32   |     Box number |
| + 0x14   |  int32   | Box set number |
| + 0x18   |  int32   |  Camera height |
| + 0x1C   |  int32   |      Sound tag |

## Data pointers:

| Location | Count |                          Type |
| :------- | :---: | ----------------------------: |
| + 0x20   | 0x01  |                Map layout (1) |
| + 0x24   | 0x14  |      Moving platform data (2) |
| + 0x74   | 0x08  |       Movable blocks data (3) |
| + 0x94   | 0x07  |                Layer data (4) |
| + 0xB0   | 0x01  |              Gimmick data (5) |
| + 0xB4   | 0x01  |                       Unknown |
| + 0xB8   | 0x01  | Moving platform path data (6) |


### (1) Map layout:

| Location | Datatype |     Name |
| :------- | :------: | -------: |
| + 0x00   |  int32   |    Width |
| + 0x04   |  int32   |   Height |
| + 0x08   |  int32   |   Count* |
| + 0x0C   |  int32   | Offset** |

\* Count is equal to Width x Height. \
\*\* Offset is the absolute offset to the actual map data.

### (2) Moving platform data:

| Location |      Datatype      |                 Name |
| :------- | :----------------: | -------------------: |
| + 0x00   |       int32        |              X start |
| + 0x04   |       int32        |              Y start |
| + 0x08   |       int32        |                X end |
| + 0x0C   |       int32        |                Y end |
| + 0x10   |       int32        | Number of blocks (n) |
| + 0x14   | (int32, int32) x n |             Unknown* |

\* Unknown block data at `+0x14` occurs `n` times, where `n` is the value at `+0x10`.

### (3) Movable blocks data:

| Location |      Datatype      |                   Name |
| :------- | :----------------: | ---------------------: |
| + 0x00   |       int32        |   Number of blocks (n) |
| + 0x04   | (int32, int32) x n | x location, y location |

Data at `+0x4` occurs `n` times, where `n` is the value at `+0x0`.

### (4) Layer data:

| Location | Datatype |     Name |
| :------- | :------: | -------: |
| + 0x00   |  int32   |   Count* |
| + 0x04   |  int32   | Offset** |

\* Count is equal to Width x Height. \
\*\* Offset is the absolute offset to the layer data. \
Note: The layers are serialized in order (0, 3, 2, 1, 4, 5, 6).

### (5) Gimmick data:

| Location |      Datatype      |         Name |
| :------- | :----------------: | -----------: |
| + 0x00   |       int32        |    Count (n) |
| + 0x04   | Gimmick (0x30) x n | Gimmick data |

Gimmick data is repeated `n` times where `n` is the value at `+0x0`.

### (6) Moving platform path data:

| Location | Datatype  |      Name |
| :------- | :-------: | --------: |
| + 0x00   |   int32   | Count (n) |
| + 0x04   | int32 x n |    Offset |

Offset is repeated `n` times where `n` is the value at `+0x0`.

Each offset points to a `MovingPlatformPath` type object which has the structure:

| Location | Datatype |     Name |
| :------- | :------: | -------: |
| + 0x00   |  int32   | Unknown0 |
| + 0x04   |  int32   | Unknown1 |
| + 0x08   |  int32   | Unknown2 |
| + 0x0C   |  int32   | Unknown3 |
| + 0x10   |  int32   | Unknown4 |
| + 0x14   |  int32   | Unknown5 |
| + 0x18   |  int32   | Unknown6 |
| + 0x1C   |  int32   | Unknown7 |


#### Gimmick data type structure:

Gimmicks have a generic structure, with a number overriding the default structure with specific types.

**Generic structure**:

| Location | Datatype |       Name |
| :------- | :------: | ---------: |
| + 0x00   |  int32   |       wuid |
| + 0x04   |  int32   |       kind |
| + 0x08   |  int32   |          x |
| + 0x0C   |  int32   |          y |
| + 0x10   |  int32   |      group |
| + 0x14   |  int32   | appearance |
| + 0x18   |  int32*  |     param0 |
| + 0x1C   |  int32*  |     param1 |
| + 0x20   |  int32*  |     param2 |
| + 0x24   |  int32*  |     param3 |
| + 0x28   |  int32*  |     param4 |
| + 0x2C   |  int32*  |     param5 |

\* The `param(n)` values may have a different data type, depending on the specific Gimmick kind.
The Gimmick kind is specified by the `kind` value at `+0x4`.

**Specific Gimmick structures**:

| Kind |          Gimmick type |
| :--- | --------------------: |
| 0    |           Spawn point |
| 1    |       Next stage door |
| 2    |       World exit door |
| 3    |                 Laser |
| 4    |                 Crown |
| 5    |                  NONE |
| 6    |                Button |
| 7    |          Toggle block |
| 8    |           Break block |
| 9    |                     ? |
| 10   |                  NONE |
| 11   |          Raising door |
| 12   |                     ? |
| 13   |             Hint area |
| 14   |                  NONE |
| 15   |                     ? |
| 16   |                  NONE |
| 17   |        Falling spikes |
| 18   |                Spikey |
| 19   |             Score dot |
| 20   |                  NONE |
| 21   |                  NONE |
| 22   |               Battery |
| 23   |            Warp cloud |
| 24   |       Crane end joint |
| 25   |                 Crane |
| 26   |      Spikey end point |
| 27   |         Gravity field |
| 28   |      World entry door |
| 29   |       Shop entry door |
| 30   |                  None |
| 31   | Black overworld smoke |
| 32   |                     ? |
| 33   |                     ? |
| 34   |                     ? |
| 35   |                 Chest |

- Laser (kind *3*)

  | Param | Datatype |   Name    |                           Description |
  | :---- | :------: | :-------: | ------------------------------------: |
  | 0     |  int32   | Direction | 2 = Down, 4 = Left, 6 = Right, 8 = Up |

- Crown (kind *4*)

- Button (kind *6*)

  | Param | Datatype |   Name    |                                                 Description |
  | :---- | :------: | :-------: | ----------------------------------------------------------: |
  | 0     |  int32   | Direction |                       2 = Down, 4 = Left, 6 = Right, 8 = Up |
  | 1     |  int32   |  Unknown  |                                                  Always 1?? |
  | 2     |  int32   |  Target   | `wuid` of the door to open when pressed,<br>or -1 to toggle |

- Battery (kind *22*)

  | Param | Datatype |    Name     |                                                  Description |
  | :---- | :------: | :---------: | -----------------------------------------------------------: |
  | 0     |  int32   |  Direction  |                                          0 = Plus, 1 = Minus |
  | 1     |  int32   | Is a Toggle |                                 0 = single use, 1 = reusable |
  | 2     |  int32   |   Target    | `wuid` of the door to open when pressed,<br>or -1 to toggle* |
    \* Only the (-) block Gimmick data needs the -1 value for Param2. The (+) block is 0 in this case.

- Warp cloud (kind *23*)

  | Param |    Datatype    |       Name       |                                                                  Description |
  | :---- | :------------: | :--------------: | ---------------------------------------------------------------------------: |
  | group |      n/a       |       n/a        |                                     Warp clouds should be paired into groups |
  | 0     |     int32      |    Direction     |                                                             0 = Up, 1 = Down |
  | 1     | (int16, int16) | Start coordinate |                                                       (initial x, initial y) |
  | 2     | (int16, int16) |    Dimensions    |                                                              (width, height) |
  | 3     |     int32      |   Linked group   | For up facing: group number to spit you out of.<br>For down facing: Always 0 |
