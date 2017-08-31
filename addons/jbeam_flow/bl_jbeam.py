import collections
from contextlib import contextmanager
from typing import Union

from bmesh.types import BMesh, BMVertSeq, BMEdgeSeq, BMFaceSeq, BMLayerItem, BMVert, BMEdge
from bpy.props import IntProperty, StringProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup, Mesh

from . import bm_props, jbeam
from .jbeam.misc import Switch

PROP_CHAIN_ID = 'jbeam_prop_chain_id'


class Counter(PropertyGroup):
    """Mimic collections.Counter, underlying data stored as ID property"""
    update = collections.Counter.update

    # Define our own method cuz dict.clear requires dict (sub)class
    def clear(self):
        ptable = getattr(self.id_data, self.path_from_id().partition('.')[0])  # type: PropsTable
        ptable['counter'].clear()  # RNA does not expose underlying ID dict property methods

    def __getitem__(self, item):
        # Blender does not call __missing__ on missing key. Thus Counter.__missing__ logic inlined here:
        if item not in self:
            return 0
        return super().__getitem__(item)


class PropsTableBase(jbeam.Table):
    """
    Represents properties inheritance chaining.
    Position in the chain described with factor (float number).
    Item with factor N inherits all props in the chain with factor less or equal to N with priority of the last.
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

    ptable_id_layer_name = None  # type: str

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
    ptable_id_layer_name = PROP_CHAIN_ID

    @classmethod
    def register(cls):
        Mesh.jbeam_node_prop_chain = PointerProperty(type=cls)
        Mesh.jbeam_beam_prop_chain = PointerProperty(type=cls)
        Mesh.jbeam_triangle_prop_chain = PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del Mesh.jbeam_node_prop_chain
        del Mesh.jbeam_beam_prop_chain
        del Mesh.jbeam_triangle_prop_chain


class UnusedNodesTable(PropertyGroup, PropsTableBase):
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


class Element(bm_props.ElemWrapper):
    """ Base class for jbeam elements (node, beam, etc.) which are represented as bmesh elements. """
    # todo: property access (ChainMap?)
    props_src = bm_props.String('JBEAM_ELEM_PROPS')


class Node(Element):
    id = bm_props.String('jbeamNodeId')

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

    @classmethod
    def ensure_data_layers(cls, bm: BMesh):
        cls.is_ghost.ensure_layer(bm.edges.layers)
        cls.props_src.ensure_layer(bm.edges.layers)

    @staticmethod
    def is_valid_type(bm_elem: bm_props.BMElem) -> bool:
        return isinstance(bm_elem, BMEdge)


class QuadsPropTable(PropertyGroup, PropsTableBase):
    ptable_id_layer_name = 'JBEAM_QUADS_PTABLE_ID'

    @staticmethod
    def get_from(mesh: Mesh):
        """
        :rtype: QuadsPropTable
        """
        return mesh.jbeam_quads_ptable

    @classmethod
    def register(cls):
        Mesh.jbeam_quads_ptable = PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del Mesh.jbeam_quads_ptable


def get_table_storage_ctxman(me, bm_elem_seq):
    """
    Returns RNA property of JbeamPropsInheritance type for given bmesh element types
    :param me: mesh that stores JbeamPropsInheritance table.
    :type me: bpy.types.Mesh
    :param bm_elem_seq: bmesh elements the table associated with.
    :type bm_elem_seq: BMVertSeq|BMEdgeSeq|BMFaceSeq
    :return: instance of table
    :rtype: JbeamPropsInheritance contextmanager
    """
    with Switch.Inst(bm_elem_seq) as case:
        if case(BMVertSeq):
            return me.jbeam_node_prop_chain.init(bm_elem_seq)
        elif case(BMEdgeSeq):
            return me.jbeam_beam_prop_chain.init(bm_elem_seq)
        elif case(BMFaceSeq):
            return me.jbeam_triangle_prop_chain.init(bm_elem_seq)
        else:
            raise ValueError('%r is not supported table storage' % bm_elem_seq)


classes = (
    Counter,
    PropsTableBase.Prop,
    PropsTable,
    QuadsPropTable,
)
