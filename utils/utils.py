from copy import copy


def check_int(value_if_allowed, allowed_values=None):
    """ Callback used to force certain entries to only allow integer value.
    They May be fixed within a set of values by specifying allowed_values.
    """
    # TODO: make allowed_values be more robust???
    if value_if_allowed == '' or value_if_allowed == '-':
        return True
    try:
        int(value_if_allowed)
    except ValueError:
        return False
    if allowed_values is not None:
        if value_if_allowed in allowed_values:
            return True
        else:
            return False
    return True


def copy_dict(dict_):
    """Return a faithful copy of a dictionary.
    This is different to a deep copy in that it will return `copy` of the
    object, unless it is a dictionary, in which case this will be called
    recursively
    """
    new_dict = dict()
    for key, value in dict_.items():
        if not isinstance(value, dict):
            new_dict[key] = copy(value)
        else:
            new_dict[key] = copy_dict(value)
    return new_dict
