import collections
from contextlib import contextmanager
from typing import Union

import bpy
from bmesh.types import BMesh, BMVertSeq, BMEdgeSeq, BMFaceSeq, BMLayerItem, BMVert, BMEdge, BMFace
from bpy.props import IntProperty, StringProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup, Mesh, Object

from . import bm_props, jbeam


class Counter(PropertyGroup):
    """Mimic collections.Counter, underlying data stored as ID property"""
    update = collections.Counter.update

    # Define our own method cuz dict.clear requires dict (sub)class
    def clear(self):
        ptable = self.id_data.path_resolve(self.path_from_id().rpartition('.')[0])  # type: PropsTable
        ptable['counter'].clear()  # RNA does not expose underlying ID dict property methods

    def __getitem__(self, item):
        # Blender does not call __missing__ on missing key. Thus Counter.__missing__ logic inlined here:
        if item not in self:
            return 0
        return super().__getitem__(item)


class PropsTableBase(jbeam.Table):
    """
    Represents properties inheritance chaining.
    Note: __init__ never called by Blender, use 'init' contextmanager instead
    """

    class Prop(PropertyGroup, jbeam.Table.Prop):
        # 'id' is a reference for nodes
        id = IntProperty()
        src = StringProperty()

    chain_list = CollectionProperty(type=Prop)
    active_index = IntProperty(default=-1)
    max_id = IntProperty()
    counter = PointerProperty(type=Counter)

    ptable_id_layer_name = 'jbeam.chain_id'

    @contextmanager
    def init(self, bm_elem_seq: Union[BMVertSeq, BMEdgeSeq, BMFaceSeq]):
        """Initialises table for creating shared properties"""
        # RNA props are already initialised.
        self._pid_key = self.get_id_layer(bm_elem_seq)
        # we should clean up bmesh stuff after exit
        try:
            yield self
        finally:
            self._pid_key = None

    def new_prop(self):
        return self.add_prop("{}")

    @classmethod
    def get_id_layer(cls, bm_elem_seq: Union[BMVertSeq, BMEdgeSeq, BMFaceSeq]) -> BMLayerItem:
        lyrs_int = bm_elem_seq.layers.int
        try:
            return lyrs_int[cls.ptable_id_layer_name]
        except KeyError:
            return lyrs_int.new(cls.ptable_id_layer_name)


class PropsTable(PropertyGroup, PropsTableBase):
    pass


class QuadsPropTable(PropertyGroup, PropsTableBase):
    ptable_id_layer_name = 'jbeam.quads.chain_id'


class Part(PropertyGroup):
    name = StringProperty(name="Name")
    slot_type = StringProperty(name="Slot type")
    data = StringProperty(name="Data", description="Partially decoded JBeam data")
    nodes = PointerProperty(type=PropsTable)
    beams = PointerProperty(type=PropsTable)
    triangles = PointerProperty(type=PropsTable)
    quads = PointerProperty(type=QuadsPropTable)

    @classmethod
    def register(cls):
        Mesh.jbeam_part = PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del Mesh.jbeam_part


class Slot(PropertyGroup):
    default = StringProperty(name="Default part", description="Default part name.")
    description = StringProperty(name="Description")

    def is_slot(self):
        return self.id_data.parent is not None and 'slots' == self.id_data.parent.name.partition('.')[0]

    def get_type(self):
        return self.id_data.name.partition('.')[0]

    def offset_update(self, _=None):
        """Apply offset to child parts."""
        obj_slot = self.id_data  # type: Object
        obj_slot.location.yz = self.nodeOffset.yz
        # X has special case [vehicle/jbeam/jbeam_main.lua:1642 - function postProcess(vehicles)]
        x_offset = self.nodeOffset.x
        for obj_part in obj_slot.children:
            mod = obj_part.modifiers.get('jbeam.slot.nodeOffset.x')  # type: bpy.types.DisplaceModifier
            if mod is None:
                mod = obj_part.modifiers.new('jbeam.slot.nodeOffset.x', 'DISPLACE')
                mod.direction = 'NORMAL'
                mod.mid_level = 0
            mod.strength = x_offset

    nodeOffset = bpy.props.FloatVectorProperty(name="Node offset", subtype='XYZ', unit='LENGTH', size=3, precision=3,
                                               update=offset_update)
    type = StringProperty(name="Type", description="Slot type.", get=get_type)

    def add_part_object(self, part: Object):
        part.parent = self.id_data
        self.offset_update()

    @classmethod
    def register(cls):
        Object.jbeam_slot = PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del Object.jbeam_slot


class _NodesTable_unused:  # (PropertyGroup, PropsTableBase):
    """ Optimise custom data accecss. """

    # not used actually, need for shut up IDE complaining
    def __init__(self):
        super().__init__()
        self._node_id_lyr = None  # type: BMLayerItem
        self._node_prop_lyr = None  # type: BMLayerItem

    @contextmanager
    def init(self, vert_seq: BMVertSeq):
        # see PropsTableBase.init for details
        with super().init(vert_seq):
            self._node_id_lyr = vert_seq.layers.string.new(Node.id.layer_name)
            self._node_prop_lyr = vert_seq.layers.string.new(Node.props_src.layer_name)
            try:
                yield self
            finally:
                self._node_id_lyr = None
                self._node_prop_lyr = None

    def new_node(self, bm: BMesh, vert: BMVert):
        if not (self._node_prop_lyr and self._node_id_lyr):
            raise ValueError("NodesTable.new method allowed only under 'with NodesTable.init()' block")

        # raise NotImplementedError()
        return Node(bm, vert)

    @property
    def node_id_lyr(self):
        return self._node_id_lyr

    @property
    def node_prop_lyr(self):
        return self._node_prop_lyr


# region BMesh element wrappers
class Element(bm_props.ElemWrapper):
    """ Base class for jbeam elements (node, beam, etc.) which are represented as bmesh elements. """
    # todo: property access (ChainMap?)
    props_src = bm_props.String('jbeam.private_props')


class Node(Element):
    id = bm_props.String('jbeam.node.id')

    def __init__(self, bm: BMesh, vert: BMVert):
        super().__init__(bm, vert)
        self.layers = bm.verts.layers

    @classmethod
    def ensure_data_layers(cls, bm: BMesh):
        cls.props_src.ensure_layer(bm.verts.layers)
        cls.id.ensure_layer(bm.verts.layers)

    @staticmethod
    def is_valid_type(bm_elem: bm_props.BMElem) -> bool:
        return isinstance(bm_elem, BMVert)


class Beam(Element):
    is_ghost = bm_props.Boolean('jbeam.beam.is_ghost')
    """True when beam is ghost, default False. 
    Ghost beams are not exported. Useful for triangles with edges which are not defined as beams."""

    def __init__(self, bm: BMesh, edge: BMEdge):
        super().__init__(bm, edge)
        self.layers = bm.edges.layers
        v1, v2 = edge.verts
        self._nodes = (Node(bm, v1), Node(bm, v2))

    @property
    def nodes(self):
        return self._nodes

    def __str__(self) -> str:
        return '["{0.id}", "{1.id}"]'.format(*self._nodes)

    @classmethod
    def ensure_data_layers(cls, bm: BMesh):
        cls.is_ghost.ensure_layer(bm.edges.layers)
        cls.props_src.ensure_layer(bm.edges.layers)

    @staticmethod
    def is_valid_type(bm_elem: bm_props.BMElem) -> bool:
        return isinstance(bm_elem, BMEdge)


class Surface(Element):
    """Collision surface: triangle or quad."""

    def __init__(self, bm: BMesh, face: BMFace):
        super().__init__(bm, face)
        self.layers = bm.faces.layers

    @classmethod
    def ensure_data_layers(cls, bm: BMesh):
        cls.props_src.ensure_layer(bm.faces.layers)

    @staticmethod
    def is_valid_type(bm_elem: bm_props.BMElem) -> bool:
        return isinstance(bm_elem, BMFace)


# endregion BMesh element wrappers


classes = (
    Counter,
    PropsTableBase.Prop,
    PropsTable,
    QuadsPropTable,
    Part,
    Slot,
)
