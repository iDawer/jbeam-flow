import types
import typing

import bmesh
import bpy
from bmesh import types as bmtypes

# Typing hints, for annotations use only.
try:
    # Blender 2.78a comes with Python 3.5.1, but typing.Type was introduced in 3.5.2
    from typing import Type
except ImportError:
    class Type(typing.Generic[typing.TypeVar('CT_co', covariant=True, bound=type)], extra=type):
        __slots__ = ()
BMElem = typing.Union[bmtypes.BMVert, bmtypes.BMEdge, bmtypes.BMFace]
BMElemSeq = typing.Union[bmtypes.BMVertSeq, bmtypes.BMEdgeSeq, bmtypes.BMFaceSeq]
BMLayerAccess = typing.Union[bmtypes.BMLayerAccessVert, bmtypes.BMLayerAccessEdge, bmtypes.BMLayerAccessFace]


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


class ABCProperty:
    def __init__(self, layer_name: str):
        self.layer_name = layer_name

    def __get__(self, instance: ElemWrapper, owner):
        raise NotImplementedError()

    def __set__(self, instance: ElemWrapper, value):
        raise NotImplementedError()

    def ensure_layer(self, layers: BMLayerAccess) -> bmtypes.BMLayerItem:
        """ Ensures data layer is initialised. Returns the layer. """
        raise NotImplementedError()

    def get_layer(self, layers: BMLayerAccess) -> bmtypes.BMLayerItem:
        """ Returns layer if exist, else returns None. """
        raise NotImplementedError()


class String(ABCProperty):
    def __init__(self, layer_name: str):
        """ :rtype: str or String """  # 'typing' module does not support des
        super().__init__(layer_name)

    def __get__(self, instance: ElemWrapper, owner):
        try:
            return instance.bm_elem[instance.layers.string[self.layer_name]].decode()
        except AttributeError:
            # '__get__' called from class
            if instance is None:
                return self
            raise  # other error occurred

    def __set__(self, instance: ElemWrapper, value: str):
        if len(value) > 255:
            raise ValueError("String value length is over than 255", value)
        instance.bm_elem[instance.layers.string[self.layer_name]] = value.encode()

    def ensure_layer(self, layers: BMLayerAccess) -> bmtypes.BMLayerItem:
        try:
            return layers.string[self.layer_name]
        except KeyError:
            return layers.string.new(self.layer_name)

    def get_layer(self, layers: BMLayerAccess) -> bmtypes.BMLayerItem:
        return layers.string.get(self.layer_name)


def make_rna_proxy(bm_prop: ABCProperty, bpy_prop, bmelem_seq_prop: types.MemberDescriptorType,
                   bmelem_type: Type[BMElem]):
    """ 
    Makes RNA porperty definition which redirects attribute access to active bmesh element's custom data. 
    This function uses RNA internals not documented in PyAPI. Tested in Blender 2.78a. 
    """
    # '_' in args is a property owner class instance
    def update(_, context):
        if context.area:
            context.area.tag_redraw()

    def setval(_, value: str):
        eo = bpy.context.edit_object
        bm = bmesh.from_edit_mesh(eo.data)
        elem = bm.select_history.active
        bmelem_seq = bmelem_seq_prop.__get__(bm)  # type: BMElemSeq
        data_layer = bm_prop.get_layer(bmelem_seq.layers)
        if elem and isinstance(elem, bmelem_type) and data_layer:
            elem[data_layer] = value.encode()

    def getval(_):
        eo = bpy.context.edit_object
        if not eo or eo.type != 'MESH':
            return ""
        bm = bmesh.from_edit_mesh(eo.data)
        elem = bm.select_history.active
        bmelem_seq = bmelem_seq_prop.__get__(bm)  # type: BMElemSeq
        data_layer = bm_prop.get_layer(bmelem_seq.layers)
        if elem and isinstance(elem, bmelem_type) and data_layer:
            return elem[data_layer].decode()
        return ""

    prop_def_args = bpy_prop[1]  # type: dict
    prop_def_args['get'] = getval
    prop_def_args['set'] = setval
    prop_def_args['update'] = update
    return bpy_prop
