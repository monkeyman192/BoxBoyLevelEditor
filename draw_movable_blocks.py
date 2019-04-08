from PIL import Image, ImageTk

from layer_data import PUSHBLOCKS


def movable_block_bound(movable_block):
    """ Return the bounds of a movable block

    Returns
    -------
    tuple
        (x_min, y_min, x_max, y_max)
    """
    return [
        min(loc[0] for loc in movable_block.block_locations),
        min(loc[1] for loc in movable_block.block_locations),
        max(loc[0] for loc in movable_block.block_locations),
        max(loc[1] for loc in movable_block.block_locations),
    ]


def movable_block_image(movable_block, existing_sprites):
    """ Return the list of sprites used to draw the movable block"""
    images = list()

    # bounds: x_min, x_max | y_min, y_max
    # First, we need to determine what sprite each location has
    for loc in movable_block.block_locations:
        ID = [
            (loc[0], loc[1] + 1) not in movable_block.block_locations,  # N
            (loc[0] + 1, loc[1]) not in movable_block.block_locations,  # E
            (loc[0], loc[1] - 1) not in movable_block.block_locations,  # S
            (loc[0] - 1, loc[1]) not in movable_block.block_locations,  # W
        ]
        # I am representing the image ID as a number based on whether each face
        # (N, E, S, W in that order) as closed off (1) or not (0).
        # Hence the binary representation (converted to base 10...)
        image_id = ID[0] * 8 + ID[1] * 4 + ID[2] * 2 + ID[3]
        if image_id in existing_sprites:
            images.append(existing_sprites[image_id])
        else:
            img = Image.open(PUSHBLOCKS[image_id]['path'])
            image = ImageTk.PhotoImage(img)
            images.append(image)
            existing_sprites[image_id] = image

    return images
