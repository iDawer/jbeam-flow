from bmesh import types as bmtypes
from typing import Union

# typing hints
BMElem = Union[bmtypes.BMVert, bmtypes.BMEdge, bmtypes.BMFace]
BMLayerAccess = Union[bmtypes.BMLayerAccessVert, bmtypes.BMLayerAccessEdge, bmtypes.BMLayerAccessFace]


# Make wrapper, because can't inherit from BMVert or other builtin types.
class ElemWrapper:
    """ 
    Abstract bmesh element wrapper class. 
    Makes it possible to use descriptors to access custom data.
    """
    def __init__(self, layers, bm_elem: BMElem):
        self.bm_elem = bm_elem  # type: BMElem
        self.layers = layers  # type: BMLayerAccess

    @classmethod
    def ensure_data_layers(cls, bm: bmtypes.BMesh):
        """ Initialise custom data layers if need. """
        raise NotImplementedError()


class String:
    def __init__(self, layer_name: str):
        """ :rtype: str or String """
        self.layer_name = layer_name

    def __get__(self, instance: ElemWrapper, owner):
        try:
            return instance.bm_elem[instance.layers.string[self.layer_name]].decode()
        except AttributeError:
            # '__get__' called from class
            if instance is None:
                return self
            raise  # other error occurred

    def __set__(self, instance: ElemWrapper, value: str):
        instance.bm_elem[instance.layers.string[self.layer_name]] = value.encode()

    def ensure_layer(self, layers: BMLayerAccess) -> bmtypes.BMLayerItem:
        """ Ensure layer is initialised """
        try:
            return layers.string[self.layer_name]
        except KeyError:
            return layers.string.new(self.layer_name)
