from collections import OrderedDict
from io import StringIO
from typing import Dict, Tuple, List, Union, Sequence

import bmesh
import bpy

from antlr4 import *  # ToDo: get rid of the global antlr4 lib
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from antlr4.tree.Tree import TerminalNodeImpl
from .jb import jbeamLexer, jbeamParser, jbeamVisitor
from .jb.utils import preprocess
from .jbeam import JbeamBase
from .jbeam.ext_json import ExtJSONParser
from .jbeam.misc import (
    Triangle,
)
from .bl_jbeam import PropsTable, get_table_storage_ctxman, QuadsPropTable

_ValueContext = ExtJSONParser.ValueContext
_ValueArrayContext = ExtJSONParser.ValueArrayContext
_ValueObjectContext = ExtJSONParser.ValueObjectContext
_ValueStringContext = ExtJSONParser.ValueStringContext


def to_tree(jbeam_data: str):
    data_stream = InputStream(jbeam_data)

    lexer = jbeamLexer(data_stream)
    stream = CommonTokenStream(lexer)
    stream = preprocess(stream)
    parser = jbeamParser(stream)
    tree = parser.jbeam()

    return tree


class PartObjectsBuilder(JbeamBase):
    lock_part_transform = True
    console_indent = 0

    def __init__(self, name='JBeam file'):
        self.name = name
        self.parts_group = None
        self.helper_objects = []
        self._vertsIndex = {}
        self._part_variables = {}
        self._vars_initialised = False

    def get_all_objects(self):
        from itertools import chain
        return chain(self.parts_group.objects, self.helper_objects)

    def jbeam(self, ctx: ExtJSONParser.JsonContext):
        jbeam_group = bpy.data.groups.new(self.name)
        self.parts_group = jbeam_group
        parts_ctx = ctx.object().pairs()
        if parts_ctx:
            for part_ctx in parts_ctx.pair():
                part_obj = self.part(part_ctx)
                jbeam_group.objects.link(part_obj)
        return jbeam_group

    def part(self, ctx: ExtJSONParser.PairContext):
        part_name, part_value_ctx = self._unpack_pair(ctx)
        self._print("part:", part_name)
        self._vertsIndex = {}
        self._part_variables = {}

        mesh = bpy.data.meshes.new(part_name)
        # Save part name explicitly, due Blender avoids names collision by appending '.001'
        mesh['jbeam_part'] = part_name
        part_obj = bpy.data.objects.new(part_name, mesh)
        part_obj.show_wire = True
        part_obj.show_all_edges = True
        if self.lock_part_transform:
            self.lock_transform(part_obj)

        data_buf = StringIO()
        sections_ctx = part_value_ctx.object().pairs()
        if sections_ctx:
            self.sections(sections_ctx, part_obj, mesh, data_buf)

        mesh['jbeam_part_data'] = data_buf.getvalue()
        mesh.update()
        return part_obj

    def sections(self, sections_ctx: ExtJSONParser.PairsContext, part_obj, mesh, data_buf: StringIO):
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
            data_pairs[s_name] = self.get_src_text_replaced(section_ctx, value_ctx, result) + ',\n'

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
    def generic_section(ctx: ExtJSONParser.ValueContext):
        # return source text
        src = ctx.parser.getTokenStream().getText(ctx.getSourceInterval())
        # escape for templating
        src = src.replace('$', '$$')
        return src

    def ensure_nodes(self, ids, bm):
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
        id_layer = bm.verts.layers.string.active
        if id_layer is None:
            # in case if no nodes section, i.e. beams with parent part nodes
            # Beware this kill existing verts in '_vertsIndex' map.
            id_layer = bm.verts.layers.string.new('jbeamNodeId')
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

    def section_slots(self, ctx: _ValueArrayContext = None, part=None, **_):
        slots_empty = bpy.data.objects.new('slots', None)
        # slot section has no transform modifiers
        self.lock_transform(slots_empty)
        slot_values_ctx = ctx.array().values()
        if slot_values_ctx:
            for prop_map, _ in self.table(slot_values_ctx):
                self._set_parent(self.slot(prop_map), slots_empty)
        self._set_parent(slots_empty, part)
        return '${slots}'

    def slot(self, props):
        name = props.pop('type') + '.slot'
        empty_obj = bpy.data.objects.new(name, None)  # 'Empty' object
        if 'nodeOffset' in props and isinstance(props['nodeOffset'], dict):
            offset = props.pop('nodeOffset')
            empty_obj.location = offset['x'], offset['y'], offset['z']
        update_id_object(empty_obj, props)
        self.lock_rot_scale(empty_obj)
        return empty_obj

    # ============================== nodes ==============================

    def section_nodes(self, ctx: _ValueArrayContext = None, me=None, bm=None, **_):
        id_layer = bm.verts.layers.string.new('jbeamNodeId')
        prop_layer = bm.verts.layers.string.new('jbeamNodeProps')
        nodes_ctx = ctx.array().values()
        if nodes_ctx:
            with get_table_storage_ctxman(me, bm.verts) as ptable:  # type: PropsTable
                for node_props, inlined_props_src in self.table(nodes_ctx, ptable):
                    node = self.node(node_props, inlined_props_src, bm, id_layer, prop_layer)
                    ptable.assign_to_last_prop(node)
        bm.verts.ensure_lookup_table()
        return '${nodes}'

    def node(self, props: dict, inlined_props_src: str, bm, id_layer, iprop_layer):
        vert = bm.verts.new((props['posX'], props['posY'], props['posZ']))
        _id = props['id']
        vert[id_layer] = _id.encode()  # set node id to the data layer
        self._vertsIndex[_id] = vert
        # inlined node props
        if inlined_props_src is not None:
            vert[iprop_layer] = inlined_props_src.encode()
        return vert

    # ============================== beams ==============================

    def section_beams(self, ctx: _ValueArrayContext = None, me=None, bm=None, **_):
        type_lyr = bm.edges.layers.int.new('jbeam_type')
        inl_props_lyr = bm.edges.layers.string.new('jbeam_prop')
        beams_ctx = ctx.array().values()
        if beams_ctx:
            with get_table_storage_ctxman(me, bm.edges) as ptable:  # type: PropsTable
                for beam_props, inl_prop_src in self.table(beams_ctx, ptable):
                    beam = self.beam(beam_props, bm, type_lyr)
                    if beam:
                        ptable.assign_to_last_prop(beam)
                        if inl_prop_src:
                            beam[inl_props_lyr] = inl_prop_src.encode()
        bm.edges.ensure_lookup_table()
        return '${beams}'

    def beam(self, props: dict, bm, beam_layer):
        id1 = props['id1:']
        id2 = props['id2:']
        nodes = self.ensure_nodes((id1, id2), bm)
        try:
            edge = bm.edges.new(nodes)  # throws on duplicates
            # set explicitly cuz triangles can have 'non beam' edges
            edge[beam_layer] = 1
            return edge
        except ValueError as err:
            self._print('\t', err, [id1, id2])  # ToDo handle duplicates
            return None

    # ============================== collision triangles ==============================

    def section_triangles(self, ctx: _ValueArrayContext = None, me=None, bm=None, **_):
        inl_props_lyr = bm.faces.layers.string.active or bm.faces.layers.string.new('jbeam_prop')
        triangles_ctx = ctx.array().values()
        if triangles_ctx:
            with get_table_storage_ctxman(me, bm.faces) as ptable:  # type: PropsTable
                for tri_prop, inl_prop_src in self.table(triangles_ctx, ptable):
                    tri = self.triangle(tri_prop, bm)
                    if tri:
                        ptable.assign_to_last_prop(tri)
                        if inl_prop_src:
                            tri[inl_props_lyr] = inl_prop_src.encode()
        bm.faces.ensure_lookup_table()
        return '${triangles}'

    def triangle(self, props: dict, bm):
        id1 = props['id1:']
        id2 = props['id2:']
        id3 = props['id3:']
        return self.face((id1, id2, id3), bm)

    def face(self, ids: Sequence[str], bm: bmesh.types.BMesh):
        nodes = self.ensure_nodes(ids, bm)
        try:
            face = bm.faces.new(nodes)
            return face
        except ValueError as err:
            self._print('\t', err, ids)  # ToDo handle duplicates
            return None

    # ============================== quads ==============================

    def section_quads(self, ctx: _ValueArrayContext = None, me=None, bm: bmesh.types.BMesh = None,
                      **_):
        inl_props_lyr = bm.faces.layers.string.active or bm.faces.layers.string.new('jbeam_prop')
        quads_ctx = ctx.array().values()
        if quads_ctx:
            with QuadsPropTable.get_from(me).init(bm.faces) as ptable:  # type: QuadsPropTable
                for prop, inl_prop_src in self.table(quads_ctx, ptable):
                    quad = self.face((prop['id1:'], prop['id2:'], prop['id3:'], prop['id4:']), bm)
                    if quad:
                        ptable.assign_to_last_prop(quad)
                        if inl_prop_src:
                            quad[inl_props_lyr] = inl_prop_src.encode()
        bm.faces.ensure_lookup_table()
        return '${triangles}'

    # ============================== another sections ==============================

    def section_slottype(self, ctx: _ValueStringContext = None, me=None, **_):
        stype = ctx.accept(self)
        me['slotType'] = stype
        return '${slotType}'


def update_id_object(id_object, props: dict):
    for k in props:
        id_object[k] = props[k]


class NodeCollector(jbeamVisitor):
    def __init__(self, part_name: str):
        super().__init__()
        self.part_name = part_name
        self.nodes = {}
        self.node_to_items_map = {}
        self.beams = {}  # key is unordered frozenset((id1, id2)) == frozenset((id2, id1))
        self.coltris = {}  # key is misc.Triangle type

    def visitPart(self, ctx: jbeamParser.PartContext):
        if ctx.name.string_item == self.part_name:
            return self.visitChildren(ctx)

    def visitNode(self, node_ctx: jbeamParser.NodeContext):
        self.nodes[node_ctx.id1.string_item] = node_ctx
        node_ctx.x = float(node_ctx.posX.text)
        node_ctx.y = float(node_ctx.posY.text)
        node_ctx.z = float(node_ctx.posZ.text)

    def visitBeam(self, beam_ctx: jbeamParser.BeamContext):
        id1, id2 = beam_ctx.id1.string_item, beam_ctx.id2.string_item
        self._link_to_node(id1, beam_ctx)
        self._link_to_node(id2, beam_ctx)
        key = frozenset((id1, id2))
        # if duplicates found, use first
        if key not in self.beams.keys():
            self.beams[key] = beam_ctx

    def _link_to_node(self, key: str, item: ParserRuleContext):
        items = self.node_to_items_map.setdefault(key, [])
        items.append(item)

    def visitColtri(self, ctx: jbeamParser.ColtriContext):
        id1 = ctx.id1.string_item
        id2 = ctx.id2.string_item
        id3 = ctx.id3.string_item
        self._link_to_node(id1, ctx)
        self._link_to_node(id2, ctx)
        self._link_to_node(id3, ctx)
        tri_key = Triangle((id1, id2, id3))
        if tri_key not in self.coltris.keys():
            self.coltris[tri_key] = ctx


jbeam_parse_tree_cache = {}


def get_parse_tree(data: str, name: str):
    # try already cached
    tree = jbeam_parse_tree_cache.get(name)
    if tree is not None:
        return tree

    data_stream = InputStream(data)
    lexer = jbeamLexer(data_stream)
    stream = CommonTokenStream(lexer)
    parser = jbeamParser(stream)
    tree = parser.jbeam()
    jbeam_parse_tree_cache[name] = tree
    return tree


class Rewriter(TokenStreamRewriter):
    def delete_subtree(self, subtree):
        self.delete(self.DEFAULT_PROGRAM_NAME, subtree.start.tokenIndex, subtree.stop.tokenIndex)
