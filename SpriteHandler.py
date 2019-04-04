def get_sprite(local_array):
    """ Return the sprite number based on the surrounding tiles. """
    kind = local_array[1][1]
    # Main ground block type
    if kind == 1:
        NW = local_array[0][0]
        N = local_array[0][1]
        NE = local_array[0][2]
        W = local_array[1][0]
        E = local_array[1][2]
        SW = local_array[2][0]
        S = local_array[2][1]
        SE = local_array[2][2]

    # Upward facing spikes
    if kind == 2:
        E = int(local_array[1][2] != 0)
        W = int(local_array[1][0] != 0)
        if E == 0 and W == 0:
            return 300  # Upward spike by itself
        if E == 1 and W == 1:
            return 301  # Upward spike surrounded on both sides
        if E == 0 and W == 1:
            return 302  # Upward right end spike
        if E == 1 and W == 0:
            return 303  # Upward left end spike

    # Downward facing spikes
    if kind == 8:
        E = int(local_array[1][2] != 0)
        W = int(local_array[1][0] != 0)
        if E == 0 and W == 0:
            return 317  # Downward spike by itself
        if E == 1 and W == 1:
            return 318  # Downward spike surrounded on both sides
        if E == 1 and W == 0:
            return 319  # Downward left end spike
        if E == 0 and W == 1:
            return 320  # Downward right end spike

    # Sticky block
    if kind == 51:
        N = int(local_array[0][1] != 0)
        W = int(local_array[1][0] != 0)
        E = int(local_array[1][2] != 0)
        S = int(local_array[2][1] != 0)
        if N == 0 and E == 1 and S == 1 and W == 0:
            return 41
        if N == 0 and E == 1 and S == 1 and W == 1:
            return 42
        if N == 0 and E == 0 and S == 1 and W == 1:
            return 43
        if N == 0 and E == 0 and S == 1 and W == 0:
            return 44
        if N == 0 and E == 1 and S == 0 and W == 0:
            return 45
        if N == 0 and E == 1 and S == 0 and W == 1:
            return 46
        if N == 0 and E == 0 and S == 0 and W == 1:
            return 47
        if N == 1 and E == 1 and S == 1 and W == 0:
            return 48
        if N == 1 and E == 1 and S == 1 and W == 1:
            return 8  # Normal ground
        if N == 1 and E == 0 and S == 1 and W == 1:
            return 50
        if N == 1 and E == 0 and S == 1 and W == 0:
            return 51
        if N == 1 and E == 1 and S == 0 and W == 0:
            return 52
        if N == 1 and E == 1 and S == 0 and W == 1:
            return 53
        if N == 1 and E == 0 and S == 0 and W == 1:
            return 54
        if N == 1 and E == 0 and S == 0 and W == 0:
            return 55
        if N == 0 and E == 0 and S == 0 and W == 0:
            return 56

    return None
