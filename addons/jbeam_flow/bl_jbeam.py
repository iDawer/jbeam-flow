import collections
import typing
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

    @staticmethod
    def link_to_scene(part_obj, scene: bpy.types.Scene):
        s_objects = scene.objects
        s_objects.link(part_obj)
        for section_obj in part_obj.children:
            s_objects.link(section_obj)
            if 'slots' == section_obj.name.partition('.')[0]:
                for slot_obj in section_obj.children:
                    s_objects.link(slot_obj)

    @staticmethod
    def get_slots(part_obj: Object):
        """
        :rtype: tuple(Object, list(Slot))
        """
        for obj in part_obj.children:
            if 'slots' == obj.name.partition('.')[0]:
                return obj, [slot_obj.jbeam_slot for slot_obj in obj.children]
        else:
            return None, []

    @classmethod
    def register(cls):
        Mesh.jbeam_part = PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del Mesh.jbeam_part


class PartsConfig(PropertyGroup):
    class Parts(dict):
        def __getitem__(self, key):
            return super().__getitem__(key)

    def __new__(cls, name, context: bpy.types.Context):
        return context.blend_data.groups.new(name).jbeam_pc

    @property
    def parts_obj(self):
        return self.id_data.objects

    @classmethod
    def register(cls):
        bpy.types.Group.jbeam_pc = PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del bpy.types.Group.jbeam_pc


class Slot(PropertyGroup):
    default = StringProperty(name="Default part", description="Default part name.")
    description = StringProperty(name="Description")

    def is_slot(self):
        return self.id_data.parent is not None and 'slots' == self.id_data.parent.name.partition('.')[0]

    def _type_get(self):
        return self.id_data.name.partition('.')[0]

    def _type_set(self, value):
        _, sep, tail = self.id_data.name.partition('.')
        self.id_data.name = sep.join((value, tail))

    @property
    def parts_obj_map(self) -> typing.Dict[str, Object]:
        """Dict[part_name: object]"""
        return {obj.data.jbeam_part.name: obj for obj in self.id_data.children}

    def offset_update(self, _=None):
        """Apply offset to child parts."""
        obj_slot = self.id_data  # type: Object
        obj_slot.location.yz = self.nodeOffset.yz
        # X has special case [vehicle/jbeam/jbeam_main.lua:1642 - function postProcess(vehicles)]
        delta_dimension = self.nodeOffset.x * 2
        for obj_part in obj_slot.children:
            mod = obj_part.modifiers.get('jbeam.slot.nodeOffset.x')
            if mod is None:
                mod = obj_part.modifiers.new('jbeam.slot.nodeOffset.x', 'DISPLACE')  # type: bpy.types.DisplaceModifier
                mod.direction = 'X'
                mod.mid_level = .5
                # texture with displace directions
                mod.texture = self._ensure_offset_texture()
            mod.strength = delta_dimension

    nodeOffset = bpy.props.FloatVectorProperty(name="Node offset", subtype='XYZ', unit='LENGTH', size=3, precision=3,
                                               update=offset_update)
    type = StringProperty(name="Type", description="Slot type.", get=_type_get, set=_type_set)

    def add_part_object(self, part: Object):
        part.parent = self.id_data
        self.offset_update()

    @staticmethod
    def _ensure_offset_texture() -> bpy.types.BlendTexture:
        t = bpy.data.textures.get('jbeam.offset')
        if t is None:
            t = bpy.data.textures.new('jbeam.offset', 'BLEND')  # type: bpy.types.BlendTexture
            t.use_fake_user = True
            t.progression = 'LINEAR'
            t.use_flip_axis = 'HORIZONTAL'
            t.use_color_ramp = True
            ramp = t.color_ramp
            ramp.color_mode = 'RGB'
            ramp.interpolation = 'CONSTANT'
            e1, e2 = ramp.elements
            e1.color = (0.0, 0.0, 0.0, 1.0)  # black, direction <0
            e2.color = (1.0, 1.0, 1.0, 1.0)  # white, direction >=0
            e2.position = .5
        return t

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
    PartsConfig,
)
