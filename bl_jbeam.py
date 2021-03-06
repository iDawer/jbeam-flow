import collections
import inspect
import typing
from contextlib import contextmanager
from typing import Type, Union

import bpy
import bpy_types
from bmesh.types import BMesh, BMVertSeq, BMEdgeSeq, BMFaceSeq, BMLayerItem, BMVert, BMEdge, BMFace
from bpy.props import IntProperty, StringProperty, BoolProperty, CollectionProperty, PointerProperty
from bpy.types import PropertyGroup, Mesh, Object

from . import bm_props, jbeam
from .bm_props import ABCProperty


# region BMesh element wrappers
class Element(bm_props.ElemWrapper):
    """ Base class for jbeam elements (node, beam, etc.) which are represented as bmesh elements. """

    _rna_info = {}
    # todo: property access (ChainMap?)
    props_src = bm_props.String('jbeam.private_props', StringProperty(name="Private properties"))


class Node(Element):
    id = bm_props.String('jbeam.node.id', StringProperty(
        name="Node id", options={'TEXTEDIT_UPDATE'}, description="Name of the node. '~' at start means it is "
                                                                 "dummy copy from parent part"))

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
    _rna_info = {'name': StringProperty(name='Name', description='Nodes of selected beam')}

    is_ghost = bm_props.Boolean('jbeam.beam.is_ghost', BoolProperty(
        name="Ghost", description="Ghost beams will not export. "
                                  "Useful for triangles with edges which are not defined as beams."))

    def __init__(self, bm: BMesh, edge: BMEdge):
        super().__init__(bm, edge)
        self.layers = bm.edges.layers
        v1, v2 = edge.verts
        self._nodes = (Node(bm, v1), Node(bm, v2))

    @property
    def nodes(self):
        return self._nodes

    @property
    def name(self) -> str:
        return str(self)

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

    _rna_info = {'name': StringProperty(name='Name', description='Nodes of selected surface')}

    def __init__(self, bm: BMesh, face: BMFace):
        super().__init__(bm, face)
        self.layers = bm.faces.layers
        self._nodes = [Node(bm, v) for v in face.verts]  # type: typing.List[Node]

    @property
    def name(self) -> str:
        return '["{}"]'.format('", "'.join((n.id for n in self._nodes)))

    @property
    def vertices(self) -> int:
        return len(self._nodes)

    @classmethod
    def ensure_data_layers(cls, bm: BMesh):
        cls.props_src.ensure_layer(bm.faces.layers)

    @staticmethod
    def is_valid_type(bm_elem: bm_props.BMElem) -> bool:
        return isinstance(bm_elem, BMFace)

# endregion BMesh element wrappers


# region Helpers

class NullablePtrMixin:
    """Emulates PointerProperty with None values.
    _nullablePtrs is dict with (property_name, null_checker_function) pairs
    """
    _nullablePtrs = {}

    def __getattribute__(self, name):
        if name != '_nullablePtrs' and name in self._nullablePtrs and self._nullablePtrs[name](self):
            return None
        return super().__getattribute__(name)


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


def _define_getset(name, prop_def, proxify: Type[Element]):
    ret_def = prop_def[0], dict(prop_def[1])
    ret_def[1]['get'] = lambda self: getattr(proxify.get_edit_active(self.id_data)[0], name)
    ret_def[1]['set'] = lambda self, val: setattr(proxify.get_edit_active(self.id_data)[0], name, val)
    return ret_def


def _prop_to_rna_prop(wrapper, pname):
    def getter(self):
        return getattr(wrapper.get_edit_active(self.id_data)[0], pname)

    rna_prop = wrapper._rna_info.get(pname)
    if rna_prop:
        rna_prop[1]['get'] = getter
        return rna_prop


class RNAProxyMeta(bpy_types.RNAMetaPropGroup):
    """Makes proxy descriptors for properties of active :class:`Element`.
    This allows exposing of :class:`Element` properties through RNA class (Blender's data).

    Data flow for ID data to display:
        bpy.data... -> RNA class -> RNA property -> UILayout.prop(..)
    Data flow for editing geometry to display:
        bpy.data... -> BMesh -> :class:`Element` -> :class:`bm_props.ABCProperty` ->
        RNA proxy class (built with :class:`RNAProxyMeta` metaclass) -> RNA property -> UILayout.prop(..)

    """

    def __new__(mcs, name, bases, namespace, proxify=None):
        if not issubclass(proxify, Element):
            raise TypeError("'proxify' must be subtype of ElemWrapper")

        cls = super().__new__(mcs, name, bases, namespace)
        for name, descr in inspect.getmembers(proxify):
            if isinstance(descr, ABCProperty):
                setattr(cls, name, _define_getset(name, descr.prop_definition, proxify))
            elif isinstance(descr, property):
                setattr(cls, name, _prop_to_rna_prop(proxify, name))

        return cls

    def __init__(cls, *args, **kwds):
        pass


# endregion Helpers

# region RNA proxy

class Proxy_ActiveNode(PropertyGroup, metaclass=RNAProxyMeta, proxify=Node):
    pass


class Proxy_ActiveBeam(PropertyGroup, metaclass=RNAProxyMeta, proxify=Beam):
    pass


class Proxy_ActiveSurface(PropertyGroup, metaclass=RNAProxyMeta, proxify=Surface):
    pass

# endregion RNA proxy


class PropsTableBase(jbeam.Table, NullablePtrMixin):
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


class NodesTable(PropsTableBase, PropertyGroup):
    _nullablePtrs = {'proxy_active': lambda self: Node.get_edit_active(self.id_data)[0] is None}
    proxy_active = PointerProperty(type=Proxy_ActiveNode)  # type: typing.Optional[Node]


class BeamsTable(PropsTableBase, PropertyGroup):
    _nullablePtrs = {'proxy_active': lambda self: Beam.get_edit_active(self.id_data)[0] is None}
    proxy_active = PointerProperty(type=Proxy_ActiveBeam)  # type: typing.Optional[Beam]


class TrianglesTable(PropsTableBase, PropertyGroup):
    def is_no_active_tri(self):
        surf = Surface.get_edit_active(self.id_data)[0]
        return surf is None or surf.vertices != 3

    _nullablePtrs = {'proxy_active': is_no_active_tri}
    proxy_active = PointerProperty(type=Proxy_ActiveSurface)  # type: typing.Optional[Surface]


class QuadsTable(PropertyGroup, PropsTableBase):
    def is_no_active_quad(self):
        surf = Surface.get_edit_active(self.id_data)[0]
        return surf is None or surf.vertices != 4

    _nullablePtrs = {'proxy_active': is_no_active_quad}
    ptable_id_layer_name = 'jbeam.quads.chain_id'
    proxy_active = PointerProperty(type=Proxy_ActiveSurface)  # type: typing.Optional[Surface]


def _id_name_decorator(rna_prop):
    def get(self: PropertyGroup):
        return self.id_data.name.partition('.')[0]

    def set(self: PropertyGroup, value):
        _, sep, tail = self.id_data.name.partition('.')
        self.id_data.name = sep.join((value, tail))

    rna_prop[1]['get'] = get
    rna_prop[1]['set'] = set
    return rna_prop


class Slot(PropertyGroup):
    type = _id_name_decorator(StringProperty(name="Type", description="Slot type."))
    default = StringProperty(name="Default part", description="Default part name.")
    description = StringProperty(name="Description")

    def is_slot(self):
        return self.id_data.parent is not None and 'slots' == self.id_data.parent.name.partition('.')[0]

    @property
    def parts_obj_map(self) -> typing.Dict[str, Object]:
        """Dict[part_name: object]"""
        return {obj.jbeam_part.name: obj for obj in self.id_data.children}

    def update_offset_correction(self, _=None):
        """Applies offset X correction to child parts using Displace modifier."""
        obj_slot = self.id_data  # type: Object
        # X has special case [vehicle/jbeam/jbeam_main.lua:1642 - function postProcess(vehicles)]
        for obj_part in obj_slot.children:
            mod = obj_part.modifiers.get('jbeam.slot.nodeOffset.x')
            if mod is None:
                mod = obj_part.modifiers.new('jbeam.slot.nodeOffset.x', 'DISPLACE')  # type: bpy.types.DisplaceModifier
                mod.direction = 'X'
                # mid_level = 1.0: white 0, black -1
                # mid_level = 0.5: white +1, black -1
                mod.mid_level = 1.0
                # texture with displace directions
                mod.texture = self._ensure_offset_texture()
            # driver setup
            fcurve = mod.driver_add('strength')
            fcurve.mute = True
            driver = fcurve.driver
            driver.type = 'SCRIPTED'
            driver.expression = "x * 2"
            var = driver.variables[0] if len(driver.variables) > 0 else driver.variables.new()
            var.type = 'TRANSFORMS'
            var.name = "x"
            var.targets[0].id = obj_slot
            var.targets[0].transform_type = 'LOC_X'
            var.targets[0].transform_space = 'WORLD_SPACE'
            fcurve.mute = False

    nodeOffset = bpy.props.FloatVectorProperty(name="Node offset", subtype='XYZ', unit='LENGTH', size=3, precision=3,
                                               step=2, get=lambda self: self.id_data.location,
                                               set=lambda self, v: setattr(self.id_data, 'location', v))

    def add_part_object(self, part_obj: Object):
        part_obj.parent = self.id_data
        self.update_offset_correction()

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


class PartGeometry(NullablePtrMixin, PropertyGroup):
    _nullablePtrs = {'proxy_active_surface': lambda self: Surface.get_edit_active(self.id_data)[0] is None}
    nodes = PointerProperty(type=NodesTable)  # type: NodesTable
    beams = PointerProperty(type=BeamsTable)  # type: BeamsTable
    triangles = PointerProperty(type=TrianglesTable)  # type: TrianglesTable
    quads = PointerProperty(type=QuadsTable)
    proxy_active_surface = PointerProperty(type=Proxy_ActiveSurface)  # type: typing.Optional[Surface]

    @classmethod
    def register(cls):
        Mesh.jbeam_pgeometry = PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del Mesh.jbeam_pgeometry


class Part(PropertyGroup):
    name = _id_name_decorator(StringProperty(name="Name"))
    slot_type = StringProperty(name="Slot type")
    data = StringProperty(name="Data", description="Partially decoded JBeam data")

    def __new__(cls, name_or_obj: Union[str, Object], context: bpy.types.Context = None):
        """
        @rtype: Part | None
        """
        if isinstance(name_or_obj, Object) and name_or_obj.type == 'MESH':
            return name_or_obj.jbeam_part
        elif isinstance(name_or_obj, str):
            mesh = context.blend_data.meshes.new(name_or_obj)
            part_obj = context.blend_data.objects.new(name_or_obj, mesh)
            part_obj.show_wire = True
            part_obj.show_all_edges = True
            from .jbeam.misc.visitor_mixins import Helper
            Helper.lock_transform(part_obj)
            # Save part name explicitly, due Blender avoids names collision by appending '.001'
            part_obj.jbeam_part.name = name_or_obj
            return part_obj.jbeam_part
        else:
            return None

    @staticmethod
    def link_to_scene(part_obj, scene: bpy.types.Scene):
        s_objects = scene.objects
        s_objects.link(part_obj)
        for section_obj in part_obj.children:
            s_objects.link(section_obj)
            if 'slots' == section_obj.name.partition('.')[0]:
                for slot_obj in section_obj.children:
                    s_objects.link(slot_obj)

    def duplicate(self):
        ob = self.id_data  # type: Object
        bpy.ops.object.select_all(action='DESELECT')
        ob.select = True
        for section_obj in ob.children:  # type: Object
            section_obj.select = True
            if 'slots' == section_obj.name.partition('.')[0]:
                for slot_obj in section_obj.children:  # type: Object
                    slot_obj.select = True
        scene_objects = bpy.context.scene.objects
        # preserve active object
        last_active, scene_objects.active = scene_objects.active, ob
        # duplicate operator preserves hierarchy, selection and active state
        bpy.ops.object.duplicate(linked=True)
        dup_ob, scene_objects.active = scene_objects.active, last_active
        return dup_ob.jbeam_part

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
        Object.jbeam_part = PointerProperty(type=cls)

    @classmethod
    def unregister(cls):
        del Object.jbeam_part


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


classes = (
    Proxy_ActiveNode,
    Proxy_ActiveBeam,
    Proxy_ActiveSurface,
    Counter,
    PropsTableBase.Prop,
    PropsTable,
    NodesTable,
    BeamsTable,
    TrianglesTable,
    QuadsTable,
    Slot,
    PartGeometry,
    Part,
    PartsConfig,
)
