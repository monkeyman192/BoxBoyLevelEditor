from PIL import Image


def apply_mods(img, mods):
    if mods is None:
        return img
    for mod in mods:
        fmt, value = mod.split('_')
        if fmt == 'rot':
            img = img.rotate(int(value))
        elif fmt == 'flip':
            if value == 'x':
                img = img.transpose(Image.FLIP_LEFT_RIGHT)
            elif value == 'y':
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
    return img
