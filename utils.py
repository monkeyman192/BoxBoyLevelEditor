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
