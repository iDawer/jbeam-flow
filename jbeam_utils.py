import io
from collections import OrderedDict, defaultdict
from typing import Dict, List, Optional, Sequence, Tuple, Union

import bmesh
import bpy
from antlr4.tree.Tree import TerminalNodeImpl

from . import bl_jbeam, jbeam
from .jbeam.ext_json import ExtJSONParser
from .jbeam.misc import (
    Triangle,
    ExtDict,
)

_ValueContext = ExtJSONParser.ValueContext
_ValueArrayContext = ExtJSONParser.ValueArrayContext
_ValueObjectContext = ExtJSONParser.ValueObjectContext
_ValueStringContext = ExtJSONParser.ValueStringContext


class VehicleBuilder:
    @classmethod
    def pc(cls, name: str, file: io.TextIOBase, context: bpy.types.Context):
        part_map = defaultdict(dict)
        for ob in context.scene.objects:
            part = bl_jbeam.Part(ob)
            if part is not None:
                slotType = part.slot_type
                part_name = part.name
                if slotType is not None and part_name is not None:
                    part_map[slotType][part_name] = ob

        main_parts = part_map.get('main')
        if not main_parts:
            raise ValueError("Missing part with slot type 'main'")
        main_obj = next(iter(main_parts.values()))
        raw_pc_data = jbeam.PC.load_from(file)
        pc = bl_jbeam.PartsConfig(name, context)
        common_objects = None
        if 'common' in context.blend_data.scenes:
            common_objects = context.blend_data.scenes['common'].objects
        cls.fill_pc_group(pc, raw_pc_data, main_obj, context, common_objects)

    @classmethod
    def fill_pc_group(cls, pc: bl_jbeam.PartsConfig, pconf: jbeam.PC, part_obj: bpy.types.Object, context,
                      common_objects: bpy.types.SceneObjects = None):
        pc.parts_obj.link(part_obj)
        slots_obj, slots = bl_jbeam.Part.get_slots(part_obj)
        slots_obj and pc.parts_obj.link(slots_obj)
        for slot in slots:
            pc.parts_obj.link(slot.id_data)
            ch_part_name = pconf.parts.get(slot.type) or slot.default
            if ch_part_name:
                # child part specified by 'pc' or default
                ch_part = slot.parts_obj_map.get(ch_part_name)
                if ch_part is not None:  # child part found
                    cls.fill_pc_group(pc, pconf, ch_part, context, common_objects)
                elif common_objects and ch_part_name in common_objects:
                    ch_part = common_objects[ch_part_name]
                    slot.add_part_object(ch_part)
                    bl_jbeam.Part.link_to_scene(ch_part, context.scene)
                    cls.fill_pc_group(pc, pconf, ch_part, context, common_objects)
                else:
                    # child part specified but not found
                    print("\tPart '{}' for slot [{}] not found".format(ch_part_name, slot.type))

    @classmethod
    def fill_slots(cls, part: bl_jbeam.Part, objects):
        part_map = defaultdict(dict)
        part_slots_map = defaultdict(list)
        for ob in objects:
            p = bl_jbeam.Part(ob)
            if p is not None:
                if p.slot_type is not None and p.name is not None:
                    part_map[p.slot_type][p.name] = ob
            elif ob.jbeam_slot.is_slot():
                part_name = ob.parent.parent.jbeam_part.name
                part_slots_map[part_name].append(ob.jbeam_slot)
        cls._fill_slots(part_map, part_slots_map, part.id_data)

    @staticmethod
    def _fill_slots(part_map: defaultdict(dict), part_slots_map: defaultdict(list), part_ob):
        _, slots = bl_jbeam.Part.get_slots(part_ob)
        for slot in slots:
            already_in_slot = slot.parts_obj_map
            for ch_part in part_map[slot.type].values():
                ch_part_name = bl_jbeam.Part(ch_part).name
                if ch_part_name in already_in_slot:
                    ch_part = already_in_slot.get(ch_part_name)
                else:
                    if ch_part.parent is not None:
                        # duplicate already parented child object
                        ch_part = bl_jbeam.Part(ch_part).duplicate().id_data
                    slot.add_part_object(ch_part)
                VehicleBuilder._fill_slots(part_map, part_slots_map, ch_part)


class PartObjectsBuilder(jbeam.EvalBase):
    lock_part_transform = True
    console_indent = 0

    def __init__(self, name='JBeam file'):
        self.name = name
        self.parts_group = None
        self.helper_objects = []
        self._vertsIndex = {}  # type: Dict[str, bmesh.types.BMVert]
        self._part_variables = {}
        self._vars_initialised = False

    def get_all_objects(self) -> Sequence[bpy.types.Object]:
        import itertools
        return itertools.chain(self.parts_group.objects if self.parts_group else [], self.helper_objects)

    def jbeam(self, ctx: ExtJSONParser.JsonContext) -> bpy.types.Group:
        jbeam_group = bpy.data.groups.new(self.name)
        self.parts_group = jbeam_group
        parts_ctx = ctx.object().pairs()
        if parts_ctx:
            for part_ctx in parts_ctx.pair():
                part_obj = self.part(part_ctx)
                jbeam_group.objects.link(part_obj)
        return jbeam_group

    def part(self, ctx: ExtJSONParser.PairContext) -> bpy.types.Object:
        part_name, part_value_ctx = self._unpack_pair(ctx)
        self._print("part:", part_name)
        self._vertsIndex = {}
        self._part_variables = {}

        part = bl_jbeam.Part(part_name, bpy.context)
        mesh = part.id_data.data  # type: bpy.types.Mesh

        data_buf = io.StringIO()
        sections_ctx = part_value_ctx.object().pairs()
        if sections_ctx:
            self.sections(sections_ctx, part.id_data, mesh, data_buf)

        part.data = data_buf.getvalue()
        mesh.update()
        return part.id_data

    def sections(self, sections_ctx: ExtJSONParser.PairsContext, part_obj, mesh, data_buf: io.StringIO):
        bm = bmesh.new()
        sections = OrderedDict((name, (value_ctx, section_ctx)) for (name, value_ctx), section_ctx in
                               ((self._unpack_pair(section_ctx), section_ctx) for section_ctx in sections_ctx.pair()))
        data_pairs = OrderedDict.fromkeys(sections.keys())

        # process variables section first
        if 'variables' in sections:
            vars_item = sections.pop('variables')
            value_ctx, section_ctx = vars_item
            self.section_variables(ctx=value_ctx)
            data_pairs['variables'] = self.get_src_text_replaced(section_ctx) + ',\n'

        for s_name, (value_ctx, section_ctx) in sections.items():
            # find section builder method
            build_section = getattr(self, 'section_' + s_name.lower(), None)
            if build_section:
                # expecting type
                exp_type = build_section.__annotations__['ctx']
                if isinstance(value_ctx, exp_type):
                    result = build_section(ctx=value_ctx, part=part_obj, me=mesh, bm=bm)
                    assert isinstance(result, str)
                else:
                    self._print("Section fallback: %s, expected %s, got %s" % (s_name, exp_type, type(value_ctx)))
                    result = self.generic_section(value_ctx)
            else:
                result = self.generic_section(value_ctx)
            data_pairs[s_name] = '    {},\n'.format(self.get_src_text_replaced(section_ctx, value_ctx, result))

        data_buf.writelines(data_pairs.values())

        bm.to_mesh(mesh)

    # ============================== utility ==============================

    def _unpack_pair(self, ctx: ExtJSONParser.PairContext) -> Tuple[str, Union[
        ExtJSONParser.ValueArrayContext,
        ExtJSONParser.ValueObjectContext,
        ExtJSONParser.ValueStringContext,
        ExtJSONParser.ValueAtomContext]
    ]:
        return ctx.STRING().accept(self), ctx.val

    def _print(self, *args):
        print('\t' * self.console_indent, *args)

    def _set_parent(self, obj, parent, prn_type='OBJECT'):
        obj.parent = parent
        obj.parent_type = prn_type
        self.helper_objects.append(obj)
        return obj

    @staticmethod
    def generic_section(ctx: ExtJSONParser.ValueContext) -> str:
        # return source text
        src = ctx.parser.getTokenStream().getText(ctx.getSourceInterval())
        # escape for templating
        src = src.replace('$', '$$')
        return src

    def ensure_nodes(self, ids, bm) -> List[bmesh.types.BMVert]:
        get_node = self._vertsIndex.get
        nodes = [get_node(id_) for id_ in ids]
        # handle dummy nodes (which not defined in prev sections)
        any_node = next((n for n in nodes if n is not None), None)  # type: bmesh.types.BMVert
        has_dummies = not all(nodes)
        if has_dummies:
            new_dummy = self.new_dummy_node
            if not any_node:
                any_node = nodes[0] = new_dummy(bm, ids[0])
            # ensure all nodes created
            nodes = [n or new_dummy(bm, ids[i], any_node.co) for i, n in enumerate(nodes)]
        return nodes

    def new_dummy_node(self, bm, dummy_id: str, co=None):
        """
        Add parent node representation to be able to store attaching beams.
        Adds '~' to the beginning of id, but _vertsIndex keeps original id.
        :type bm: bmesh.types.BMesh
        :param dummy_id: string
        :param co: mathutils.Vector
        :return: bmesh.types.BMVert
        """
        # Init in case if no nodes section, i.e. beams with parent part nodes
        # Beware it kills existing verts in '_vertsIndex' map.
        id_layer = bl_jbeam.Node.id.ensure_layer(bm.verts.layers)

        if co:
            vert = bm.verts.new(co)
            # hang dummy node
            vert.co.z -= .3
        else:
            vert = bm.verts.new((.0, .0, .0))
        vert[id_layer] = ''.join(('~', dummy_id)).encode()
        self._vertsIndex[dummy_id] = vert
        return vert

    # ============================== variables ===============================

    def section_variables(self, ctx: _ValueArrayContext, **_):
        self._vars_initialised = False
        vars_ctx = ctx.array().values()
        if vars_ctx:
            self._part_variables.update((var['name'], var) for var, _ in self.table(vars_ctx))
        self._vars_initialised = True
        return  # '${variables}'

    def visitTerminal(self, tnode: TerminalNodeImpl):
        value = super().visitTerminal(tnode)
        if self._vars_initialised and tnode.symbol.type == ExtJSONParser.STRING and value.startswith('$'):
            return self._part_variables[value]['default']
        return value

    # ============================== slots ==============================

    def section_slots(self, ctx: _ValueArrayContext = None, part=None, **_) -> str:
        slots_empty = bpy.data.objects.new('slots', None)
        # slot section has no transform modifiers
        self.lock_transform(slots_empty)
        slot_values_ctx = ctx.array().values()
        if slot_values_ctx:
            for prop_map, _ in self.table(slot_values_ctx):
                self._set_parent(self.slot(prop_map), slots_empty)
        self._set_parent(slots_empty, part)
        return '${slots}'

    def slot(self, props: ExtDict) -> bpy.types.Object:
        name = props.pop('type') + '.slot'
        empty_obj = bpy.data.objects.new(name, None)  # 'Empty' object
        self.lock_transform(empty_obj)
        slot = empty_obj.jbeam_slot  # type: bl_jbeam.Slot
        if 'nodeOffset' in props and isinstance(props['nodeOffset'], dict):
            offset = props.pop('nodeOffset')
            slot.nodeOffset = offset['x', 'y', 'z']
        slot.default, slot.description = props['default', 'description']
        return empty_obj

    # ============================== nodes ==============================

    def section_nodes(self, ctx: _ValueArrayContext = None, me=None, bm: bmesh.types.BMesh = None, **_) -> str:
        bl_jbeam.Node.ensure_data_layers(bm)
        nodes_ctx = ctx.array().values()
        if nodes_ctx:
            with me.jbeam_pgeometry.nodes.init(bm.verts) as ptable:  # type: bl_jbeam.PropsTable
                for node_props, inlined_props_src in self.table(nodes_ctx, ptable):
                    node = self.node(node_props, inlined_props_src, bm)
                    ptable.assign_to_last_prop(node)
        bm.verts.ensure_lookup_table()
        return '${nodes}'

    def node(self, props: ExtDict, inlined_props_src: str, bm):
        vert = bm.verts.new(props['posX', 'posY', 'posZ'])
        node = bl_jbeam.Node(bm, vert)
        _id = props['id']
        node.id = _id
        self._vertsIndex[_id] = vert
        # inlined node props
        if inlined_props_src is not None:
            node.props_src = inlined_props_src
        return vert

    # ============================== beams ==============================

    def section_beams(self, ctx: _ValueArrayContext = None, me=None, bm=None, **_) -> str:
        bl_jbeam.Beam.ensure_data_layers(bm)
        beams_ctx = ctx.array().values()
        if beams_ctx:
            with me.jbeam_pgeometry.beams.init(bm.edges) as ptable:  # type: bl_jbeam.PropsTable
                for beam_props, inl_prop_src in self.table(beams_ctx, ptable):
                    beam = self.beam(beam_props, inl_prop_src, bm)
                    if beam:
                        ptable.assign_to_last_prop(beam.bm_elem)
        bm.edges.ensure_lookup_table()
        return '${beams}'

    def beam(self, props: ExtDict, inlined_props_src: str, bm) -> Optional[bl_jbeam.Beam]:
        ids = props['id1:', 'id2:']
        nodes = self.ensure_nodes(ids, bm)
        try:
            edge = bm.edges.new(nodes)  # throws on duplicates
            beam = bl_jbeam.Beam(bm, edge)
            if inlined_props_src is not None:
                beam.props_src = inlined_props_src
            return beam
        except ValueError as err:
            self._print('\t', err, list(ids))  # ToDo handle duplicates
            return None

    # ============================== collision triangles ==============================

    def section_triangles(self, ctx: _ValueArrayContext = None, me=None, bm=None, **_) -> str:
        bl_jbeam.Surface.ensure_data_layers(bm)
        triangles_ctx = ctx.array().values()
        if triangles_ctx:
            with me.jbeam_pgeometry.triangles.init(bm.faces) as ptable:  # type: bl_jbeam.PropsTable
                for tri_prop, inl_prop_src in self.table(triangles_ctx, ptable):
                    surface = self.surface(tri_prop['id1:', 'id2:', 'id3:'], inl_prop_src, bm)
                    if surface:
                        ptable.assign_to_last_prop(surface.bm_elem)
        bm.faces.ensure_lookup_table()
        return '${triangles}'

    def surface(self, ids: Sequence[str], priv_props_src: str, bm: bmesh.types.BMesh) -> Optional[bl_jbeam.Surface]:
        nodes = self.ensure_nodes(ids, bm)
        # handle ghost beams
        edge_pairs = zip(nodes, nodes[1:] + nodes[:1])
        ghost_edge_pairs = (pair for pair in edge_pairs if bm.edges.get(pair) is None)
        try:
            face = bm.faces.new(nodes)
            surface = bl_jbeam.Surface(bm, face)
            if priv_props_src is not None:
                surface.props_src = priv_props_src
            for pair in ghost_edge_pairs:
                edge = bm.edges.get(pair)
                ghost_beam = bl_jbeam.Beam(bm, edge)
                ghost_beam.is_ghost = True
            return surface
        except ValueError as err:
            self._print('\t', err, ids)  # ToDo handle duplicates
            return None

    # ============================== quads ==============================

    def section_quads(self, ctx: _ValueArrayContext = None, me=None, bm: bmesh.types.BMesh = None, **_) -> str:
        bl_jbeam.Surface.ensure_data_layers(bm)
        quads_ctx = ctx.array().values()
        if quads_ctx:
            with me.jbeam_pgeometry.quads.init(bm.faces) as ptable:  # type: bl_jbeam.QuadsTable
                for prop, inl_prop_src in self.table(quads_ctx, ptable):
                    surface = self.surface(prop['id1:', 'id2:', 'id3:', 'id4:'], inl_prop_src, bm)
                    if surface:
                        ptable.assign_to_last_prop(surface.bm_elem)
        bm.faces.ensure_lookup_table()
        return '${quads}'

    # ============================== another sections ==============================

    def section_slottype(self, ctx: _ValueStringContext = None, part=None, **_) -> str:
        stype = ctx.accept(self)
        bl_jbeam.Part(part).slot_type = stype
        return '${slotType}'


class JbeamExporter:
    @staticmethod
    def process(jbeam_name: str, context: bpy.types.Context, io_out: io.StringIO):
        jb_group = context.blend_data.groups.get(jbeam_name)  # type: bpy.types.Group
        io_out.write('{\n')
        if jb_group:
            for part_obj in jb_group.objects:  # type: bpy.types.Object
                part = bl_jbeam.Part(part_obj)
                JbeamExporter.part(part, io_out)
        io_out.write('}\n')

    @staticmethod
    def part(part: bl_jbeam.Part, io_out: io.StringIO):
        data = {
            '${slotType}': '"{}"'.format(part.slot_type),
            '${slots}': '{}',
            '${nodes}': '{}',
            '${beams}': '{}',
            '${triangles}': '{}',
            '${quads}': '{}'
        }

        str_data = part.data  # type: str
        for key, val in data.items():
            str_data = str_data.replace(key, val)
        io_out.write('"{0}": {{\n{1}}},\n'.format(part.name, str_data))

    @staticmethod
    def slots(part: bl_jbeam.Part) -> str:
        part_obj = part.id_data
        _, slots = bl_jbeam.Part.get_slots(part_obj)
        for slot in slots:

            pass


classes = ()
