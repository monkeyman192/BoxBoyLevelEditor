import os.path as op
import os
import json


class Settings():
    """ Settings handler object.

    Parameters
    ----------
    fname : str
        File path to settings file (or where it should be).
    """
    def __init__(self, fname):
        # ensure the folder exists.
        if not op.exists(op.dirname(fname)):
            os.makedirs(op.dirname(fname))
        self.fname = fname

    def read(self, setting):
        if not op.exists(self.fname):
            return None
        with open(self.fname, 'r') as f:
            try:
                data = json.load(f)
                return data.get(setting)
            except json.JSONDecodeError:
                return None

    def readall(self):
        if not op.exists(self.fname):
            return None
        with open(self.fname, 'r') as f:
            return json.load(f)

    def write(self, settings):
        """
        Parameters
        ----------
        settings : dict
            Dictionary of values to update the current settings with
        """
        if not op.exists(self.fname):
            with open(self.fname, 'w') as f:
                json.dump(settings, f)
        else:
            with open(self.fname, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = dict()
            data.update(settings)
            with open(self.fname, 'w') as f:
                json.dump(data, f)
