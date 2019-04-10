from PIL import Image, ImageTk

from layer_data import PUSHBLOCKS


def pushblock_bound(pushblock):
    """ Return the bounds of a pushblock

    Returns
    -------
    tuple
        (x_min, y_min, x_max, y_max)
    """
    return [
        min(loc[0] for loc in pushblock.block_locations),
        min(loc[1] for loc in pushblock.block_locations),
        max(loc[0] for loc in pushblock.block_locations),
        max(loc[1] for loc in pushblock.block_locations),
    ]


def update_bounds(pushblock, data, parent):
    bounds = pushblock_bound(pushblock)
    ID = parent.canvas.create_rectangle(
        32 * bounds[0],
        32 * (parent.height - bounds[1]),
        32 * (bounds[2] + 1),
        32 * (parent.height - bounds[3] - 1),
        fill='', width=3, outline='#FF0000')
    data['bounds'] = ID

    return ID


def update_pushblock_sprites(pushblock, group, parent):
    pb_imgs = pushblock_image(pushblock, parent.pushblock_sprites)
    for i, ID in enumerate(parent.pushblock_data[group]['ids']):
        image = pb_imgs[i]
        if image != parent.pushblock_tiles[ID]:
            # remove the old image
            parent.canvas.delete(ID)
            # Add a new one and replace the old data
            new_ID = parent.canvas.create_image(
                32 * pushblock.block_locations[i][0],
                32 * (parent.height - pushblock.block_locations[i][1]),
                image=image,
                tags='PUSHBLOCK_{0}'.format(str(i)),
                anchor='sw')
            parent.pushblock_data[group]['ids'][i] = new_ID
            del parent.pushblock_tiles[ID]
            parent.pushblock_tiles[new_ID] = image


def pushblock_image(pushblock, existing_sprites):
    """ Return the list of sprites used to draw the pushblock"""

    if pushblock is None:
        # Return just the solid block
        if 15 in existing_sprites:
            return existing_sprites[15]
        img = Image.open(PUSHBLOCKS[15]['path'])
        image = ImageTk.PhotoImage(img)
        existing_sprites[15] = image
        return image

    images = list()

    # bounds: x_min, x_max | y_min, y_max
    # First, we need to determine what sprite each location has
    for loc in pushblock.block_locations:
        ID = [
            (loc[0], loc[1] + 1) not in pushblock.block_locations,  # N
            (loc[0] + 1, loc[1]) not in pushblock.block_locations,  # E
            (loc[0], loc[1] - 1) not in pushblock.block_locations,  # S
            (loc[0] - 1, loc[1]) not in pushblock.block_locations,  # W
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
