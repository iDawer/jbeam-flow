from .triangle import Triangle
from .Switch import Switch
from . import visitor_mixins
from . import anytree


class ExtDict(dict):
    """Extended dictionary: items access by tuple of keys """

    def __missing__(self, key):
        """Tries to return tuple of values according to tuple of keys"""
        if isinstance(key, tuple):
            getitem_ = super().__getitem__
            return tuple(getitem_(k) for k in key)
        raise KeyError(key)
