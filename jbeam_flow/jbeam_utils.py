from io import StringIO
from types import GeneratorType
from typing import Tuple, List, Union

import bmesh
import bpy
from bpy.types import Object as IDObject

from antlr4 import *  # ToDo: get rid of the global antlr4 lib
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from .jb import jbeamLexer, jbeamParser, jbeamVisitor
from .jb.utils import preprocess
from .jbeam import JbeamBase
from .jbeam.ext_json import ExtJSONParser
from .jbeam.misc import (
    Triangle,
    Switch,
    visitor_mixins as vmix,
)
from .props_inheritance import PropInheritanceBuilder

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


class PartObjectsBuilder(JbeamBase, vmix.Helper, jbeamVisitor):
    lock_part_transform = True
    console_indent = 0

    def __init__(self, name='JBeam file'):
        self.name = name
        self.parts_group = None
        self.helper_objects = []
        self._vertsIndex = None

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

    def sections(self, sections_ctx: ExtJSONParser.PairsContext, part_obj, mesh, data_buf):
        bm = bmesh.new()
        for section_ctx in sections_ctx.pair():
            s_name, value_ctx = self._unpack_pair(section_ctx)
            # find section builder method
            build_section = getattr(self, 'section_' + s_name.lower(), None)
            if build_section:
                # expecting type
                exp_type = build_section.__annotations__['ctx']
                if isinstance(value_ctx, exp_type):
                    result = build_section(value_ctx)
                    with Switch(type(result)) as case:
                        if case(tuple):  # IDObject
                            self._set_parent(result[0], part_obj)
                            result = result[1]
                        elif case(GeneratorType):
                            result.send(None)  # charge generator
                            # generator returns a placeholder text
                            gen_res = result.send((bm, mesh))
                            result = gen_res[0]
                            # if len(gen_res) == 3:
                            #     # ID property
                            #     mesh[gen_res[1]] = gen_res[2]
                        elif case(str):
                            # other sections
                            pass
                        else:
                            raise ValueError("Section not implemented")
                else:
                    self._print("Section fallback: %s, expected %s, got %s" % (s_name, exp_type, type(value_ctx)))
                    result = self.generic_section(value_ctx)
            else:
                result = self.generic_section(value_ctx)

            data = self.get_src_text_replaced(section_ctx, value_ctx, result)
            data_buf.write(data)
            data_buf.write('\n')

        bm.to_mesh(mesh)

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

    def generic_section(self, ctx: ExtJSONParser.ValueContext):
        # return source text
        src = ctx.parser.getTokenStream().getText(ctx.getSourceInterval())
        # escape for templating
        src = src.replace('$', '$$')
        return src

    # ============================== slots ==============================

    def section_slots(self, ctx: _ValueArrayContext):
        slots_empty = bpy.data.objects.new('slots', None)
        # slot section has no transform modifiers
        self.lock_transform(slots_empty)
        slot_values_ctx = ctx.array().values()
        if slot_values_ctx:
            header, row_ctx_iter = self.table(slot_values_ctx)
            for row_ctx in row_ctx_iter:
                self.slot(header, row_ctx, slots_empty)
        return slots_empty, '${slots}'

    def slot(self, header, ctx: _ValueArrayContext, slots_obj):
        slot_row = ctx.accept(self)
        props = self.row_to_map(header, slot_row)
        name = props.pop('type') + '.slot'
        slot = bpy.data.objects.new(name, None)  # 'Empty' object
        offset = props.pop('nodeOffset', None)
        if offset is not None:
            slot.location = offset['x'], offset['y'], offset['z']
        update_id_object(slot, props)
        self.lock_rot_scale(slot)
        self._set_parent(slot, slots_obj)
        return slot

    def _asdasdvisitChildren(self, node, aggregator=None):
        for c in node.getChildren():
            if not self.shouldVisitNextChild(node, aggregator):
                return

            child_result = c.accept(self)
            if child_result is None:
                continue
            with Switch(type(child_result)) as case:
                if case(GeneratorType):
                    child_result.send(None)  # charge generator
                    child_result.send(aggregator)
                elif case(tuple):
                    # treat as key val setter
                    if aggregator is None:
                        aggregator = {}
                    if len(child_result) == 3:
                        # attr setter
                        rna, attr, val = child_result
                        setattr(aggregator, attr, val)
                    else:
                        # dict
                        key, val = child_result
                        aggregator[key] = val
                elif case(IDObject):
                    # suppose aggregator is IDObject too
                    self._set_parent(child_result, aggregator)
                else:
                    if aggregator is None:
                        aggregator = []
                    aggregator.append(child_result)

        return aggregator

    def visitSlotProp_CoreSlot(self, ctx: jbeamParser.SlotProp_CoreSlotContext):
        return 'coreSlot', ctx.core.accept(self)

    def visitSlotProp_NodeOffset(self, ctx: jbeamParser.SlotProp_NodeOffsetContext):
        return 'RNA', 'location', ctx.node_offset.accept(self)

    def visitOffset(self, ctx: jbeamParser.OffsetContext):
        offset = {'x': 0, 'y': 0, 'z': 0}

        def blabla(axis):
            if isinstance(axis, jbeamParser.OffsetAxisXContext):
                offset['x'] = float(axis.x.text)
            elif isinstance(axis, jbeamParser.OffsetAxisYContext):
                offset['y'] = float(axis.y.text)
            elif isinstance(axis, jbeamParser.OffsetAxisZContext):
                offset['z'] = float(axis.z.text)

        blabla(ctx.ax1)
        blabla(ctx.ax2)
        blabla(ctx.ax3)
        return offset['x'], offset['y'], offset['z']

    # ============================== nodes ==============================

    def section_nodes(self, ctx: _ValueArrayContext):
        bm, me = yield  # bmesh
        id_layer = bm.verts.layers.string.new('jbeamNodeId')
        prop_inh = PropInheritanceBuilder(bm.verts, me.jbeam_node_prop_chain)
        prop_layer = bm.verts.layers.string.new('jbeamNodeProps')
        nodes_ctx = ctx.array().values()
        if nodes_ctx:
            header, row_ctx_iter = self.table(nodes_ctx)
            for row_ctx in row_ctx_iter:
                with Switch.Inst(row_ctx) as case:
                    if case(_ValueArrayContext):
                        self.node(header, row_ctx, bm, id_layer, prop_layer, prop_inh)
                    elif case(_ValueObjectContext):
                        self.row_shared_prop(row_ctx, prop_inh)
                    else:
                        # other types in a table not supported, ignore them
                        return
        bm.verts.ensure_lookup_table()
        yield '${nodes}'

    def node(self, header, ctx: _ValueArrayContext, bm, id_layer, prop_layer, prop_inh):
        row = ctx.accept(self)
        prop = self.row_to_map(header, row)
        vert = bm.verts.new((prop['posX'], prop['posY'], prop['posZ']))
        _id = prop['id']
        vert[id_layer] = _id.encode()  # set node id to the data layer
        self._vertsIndex[_id] = vert
        # inlined node props
        iprop_src = self.get_inlined_props_src(header, ctx)
        if iprop_src is not None:
            vert[prop_layer] = iprop_src.encode()
        prop_inh.next_item(vert)
        return vert

    def row_shared_prop(self, ctx: _ValueObjectContext, prop_inh):
        src = self.get_src_text_replaced(ctx)
        prop_inh.next_prop(src)

    # ============================== beams ==============================

    def section_beams(self, ctx: _ValueArrayContext):
        bm, me = yield
        beam_layer = bm.edges.layers.int.new('jbeam')
        prop_inh = PropInheritanceBuilder(bm.edges, me.jbeam_beam_prop_chain)
        beams_ctx = ctx.array().values()
        if beams_ctx:
            header, row_ctx_iter = self.table(beams_ctx)
            for row_ctx in row_ctx_iter:
                with Switch.Inst(row_ctx) as case:
                    if case(_ValueArrayContext):
                        self.beam(header, row_ctx, bm, beam_layer, prop_inh)
                    elif case(_ValueObjectContext):
                        self.row_shared_prop(row_ctx, prop_inh)
                    else:
                        pass  # ignore other types
        bm.edges.ensure_lookup_table()
        yield '${beams}'

    def beam(self, header, ctx: _ValueArrayContext, bm, beam_layer, prop_inh):
        row = ctx.accept(self)
        prop = self.row_to_map(header, row)
        id1 = prop['id1:']
        id2 = prop['id2:']
        v1, v2 = self._vertsIndex.get(id1), self._vertsIndex.get(id2)
        # check for attaching to parent
        if not (v1 or v2):
            # both belong to parent? ok
            v1 = self.new_dummy_node(bm, id1)
            v2 = self.new_dummy_node(bm, id2, v1.co)
        elif not v1:
            # v1 belongs to parent
            v1 = self.new_dummy_node(bm, id1, v2.co)
        elif not v2:
            v2 = self.new_dummy_node(bm, id2, v1.co)

        try:
            edge = bm.edges.new((v1, v2))  # throws on duplicates
            # set explicitly cuz triangles can have 'non beam' edges
            edge[beam_layer] = 1
            # todo beam inlined props
            prop_inh.next_item(edge)
            return edge
        except ValueError as err:
            self._print('\t', err, [id1, id2])  # ToDo handle duplicates
            return None

    def new_dummy_node(self, bm, dummy_id: str, co=None):
        """
        Add parent node representation to be able to store attaching beams.
        Adds '~' to the beginning of id, but _vertsIndex keeps original id.
        :param bm: bmesh
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

    # ============================== collision triangles ==============================

    def section_triangles(self, ctx: _ValueArrayContext):
        bm, me = yield
        prop_inh = PropInheritanceBuilder(bm.faces, me.jbeam_triangle_prop_chain)
        triangles_ctx = ctx.array().values()
        if triangles_ctx:
            header, row_ctx_iter = self.table(triangles_ctx)
            for row_ctx in row_ctx_iter:
                with Switch.Inst(row_ctx) as case:
                    if case(_ValueArrayContext):
                        self.triangle(header, row_ctx, bm, prop_inh)
                    elif case(_ValueObjectContext):
                        self.row_shared_prop(row_ctx, prop_inh)
        bm.faces.ensure_lookup_table()
        yield '${triangles}'

    def triangle(self, header, ctx: _ValueArrayContext, bm, prop_inh):
        row = ctx.accept(self)
        prop = self.row_to_map(header, row)
        id1 = prop['id1:']
        id2 = prop['id2:']
        id3 = prop['id3:']
        v_cache = self._vertsIndex
        v1, v2, v3 = v_cache.get(id1), v_cache.get(id2), v_cache.get(id3)

        # handle dummy nodes (which not in the beams section)
        any_tnode = v1 or v2 or v3
        has_dummies = not (v1 and v2 and v3)
        if has_dummies:
            if not any_tnode:
                any_tnode = v1 = self.new_dummy_node(bm, id1)
            if not v1:
                v1 = self.new_dummy_node(bm, id1, any_tnode.co)
            if not v2:
                v2 = self.new_dummy_node(bm, id2, any_tnode.co)
            if not v3:
                v3 = self.new_dummy_node(bm, id3, any_tnode.co)

        try:
            face = bm.faces.new((v1, v2, v3))
            prop_inh.next_item(face)
            return face
        except ValueError as err:
            self._print('\t', err, [id1, id2, id3])  # ToDo handle duplicates
            return None

    # ============================== another sections ==============================

    def section_slottype(self, ctx: _ValueStringContext):
        bm, me = yield
        stype = ctx.accept(self)
        me['slotType'] = stype
        yield '${slotType}'


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