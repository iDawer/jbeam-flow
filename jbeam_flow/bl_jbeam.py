from contextlib import contextmanager
from typing import Union

from bmesh.types import BMVertSeq, BMEdgeSeq, BMFaceSeq, BMLayerItem, BMesh
from bpy.props import IntProperty, StringProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup, Mesh

from .jbeam import Table, Switch

PROP_CHAIN_ID = 'jbeam_prop_chain_id'


class PropsTableBase(Table):
    """
    Represents properties inheritance chaining.
    Position in the chain described with factor (float number).
    Item with factor N inherits all props in the chain with factor less or equal to N with priority of the last.
    Note: __init__ never called by Blender, use 'init' contextmanager instead
    """

    class Prop(PropertyGroup, Table.Prop):
        # 'id' is a reference for nodes
        id = IntProperty()
        src = StringProperty()

    chain_list = CollectionProperty(type=Prop)
    active_index = IntProperty(default=-1)
    max_id = IntProperty()

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

    def new(self):
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


class QuadsPropTable(PropertyGroup, PropsTableBase):
    ptable_id_layer_name = 'JBEAM_QUADS_PTABLE_ID'

    @staticmethod
    def get_from(mesh: Mesh):
        """
        :rtype: QuadsPropTable
        """
        return mesh.jbeam_quads_ptable


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


class Unused_PropInheritanceBuilder:
    def __init__(self, bm_elem_seq, props_inh: PropsTable):
        self._last_prop_id = 0
        # property inheritance factor
        # 0 - not affected with property inheritance
        self._current_f = 0.0
        self.step = 100.0
        # A node inherits properties step by step from 0 (nothing) to last factor <= vert[_lyr]
        self._lyr = bm_elem_seq.layers.int.new(PROP_CHAIN_ID)
        self.props_inh = props_inh  # JbeamPropsInheritance

    def next_item(self, bm_elem):
        bm_elem[self._lyr] = self._last_prop_id

    def next_prop(self, src):
        self._current_f += self.step
        prop = self.props_inh.add(self._current_f, src)
        self._last_prop_id = prop.id


def register():
    Mesh.jbeam_node_prop_chain = PointerProperty(type=PropsTable)
    Mesh.jbeam_beam_prop_chain = PointerProperty(type=PropsTable)
    Mesh.jbeam_triangle_prop_chain = PointerProperty(type=PropsTable)
    Mesh.jbeam_quads_ptable = PointerProperty(type=QuadsPropTable)


def unregister():
    del Mesh.jbeam_node_prop_chain
    del Mesh.jbeam_beam_prop_chain
    del Mesh.jbeam_triangle_prop_chain
    del Mesh.jbeam_quads_ptable
