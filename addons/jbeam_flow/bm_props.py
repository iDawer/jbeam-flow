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

    def __init__(self, bm: bmtypes.BMesh, bm_elem: BMElem):
        self.bm_elem = bm_elem  # type: BMElem
        self.layers = None  # type: BMLayerAccess

    @staticmethod
    def is_valid_type(bm_elem: BMElem) -> bool:
        raise NotImplementedError()

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
        except AttributeError:  # This seems to be buggy when there is no data layer.
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


class Boolean(ABCProperty):
    def __init__(self, layer_name: str):
        """ :rtype: bool or Boolean """  # 'typing' module does not support des
        super().__init__(layer_name)

    def __get__(self, instance: ElemWrapper, owner):
        try:
            return bool(instance.bm_elem[instance.layers.int[self.layer_name]])
        except AttributeError:  # This seems to be buggy when there is no data layer.
            # '__get__' called from class
            if instance is None:
                return self
            raise  # other error occurred

    def __set__(self, instance: ElemWrapper, value: bool):
        instance.bm_elem[instance.layers.int[self.layer_name]] = int(value)

    def ensure_layer(self, layers: BMLayerAccess) -> bmtypes.BMLayerItem:
        try:
            return layers.int[self.layer_name]
        except KeyError:
            return layers.int.new(self.layer_name)

    def get_layer(self, layers: BMLayerAccess) -> bmtypes.BMLayerItem:
        return layers.int.get(self.layer_name)


def make_rna_proxy(wrapper_t: Type[ElemWrapper], bm_prop: ABCProperty, bpy_prop):
    """ 
    Makes RNA porperty definition which redirects attribute access to active bmesh element's custom data. 
    This function uses RNA internals not documented in PyAPI. Tested in Blender 2.78a. 
    :param wrapper_t: implemented ElemWrapper class
    :param bm_prop: bm elem property to proxy.
    :param bpy_prop: base RNA property (description, options).
    :return: 
    """

    # '_' in args is a property owner class instance
    def update(_, context):
        if context.area:
            context.area.tag_redraw()

    getter_sentinel = object()

    # Note: Blender 2.78a suppresses exceptions raised inside get/set functions.
    def getset(_, value=getter_sentinel):
        # exception suppressing workaround
        global last_error
        last_error = None

        eo = bpy.context.edit_object
        if not eo or eo.type != 'MESH':
            raise NoEditMeshError("There is no edit mesh in the context.")
        bm = bmesh.from_edit_mesh(eo.data)
        elem = bm.select_history.active
        if wrapper_t.is_valid_type(elem):
            wrapped = wrapper_t(bm, elem)
            wrapped.ensure_data_layers(bm)
            if value is getter_sentinel:
                return bm_prop.__get__(wrapped, wrapper_t)
            else:
                bm_prop.__set__(wrapped, value)
        else:
            raise ElementTypeError("Active mesh element has inappropriate type: {}".format(elem))

    prop_def_args = bpy_prop[1]  # type: dict
    prop_def_args['get'] = lambda _: getset(_)  # Blender requires exactly 1 argument
    prop_def_args['set'] = getset
    prop_def_args['update'] = update
    return bpy_prop


# Last error raised by rna proxy
last_error = None  # type: Error


class Error(Exception):
    def __init__(self, message):
        self.message = message
        global last_error
        last_error = self


class NoEditMeshError(Error):
    pass


class ElementTypeError(Error):
    """Raised when type of active mesh element is wrong"""
    pass


classes = ()
