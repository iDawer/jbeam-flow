from types import GeneratorType
from io import StringIO

import bpy
from bpy.types import Object as IDObject
import bmesh

from antlr4 import *  # ToDo: get rid of the global antlr4 lib
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from .jb import jbeamLexer, jbeamParser, jbeamVisitor
from .misc import (
    Triangle,
    Switch,
    visitor_mixins as vmix,
)


def to_tree(jbeam_data: str):
    data_stream = InputStream(jbeam_data)

    lexer = jbeamLexer(data_stream)
    stream = CommonTokenStream(lexer)
    parser = jbeamParser(stream)
    tree = parser.jbeam()

    return tree


class PartObjectsBuilder(vmix.Json, vmix.Helper, jbeamVisitor):
    def __init__(self, name='JBeam file'):
        self.name = name
        self.parts_group = None
        self.helper_objects = []
        self._vertsIndex = None

    def get_all_objects(self):
        from itertools import chain
        return chain(self.parts_group.objects, self.helper_objects)

    def visitJbeam(self, ctx: jbeamParser.JbeamContext):
        jbeam_group = bpy.data.groups.new(self.name)
        self.parts_group = jbeam_group
        if ctx.listt is not None:
            for part_ctx in ctx.listt.getChildren():
                part_obj = part_ctx.accept(self)
                jbeam_group.objects.link(part_obj)
        return jbeam_group

    def visitPart(self, ctx: jbeamParser.PartContext):
        part_name = ctx.name.string_item
        print('part: ' + part_name)
        self._vertsIndex = {}

        mesh = bpy.data.meshes.new(part_name)
        # Save part name explicitly, due Blender avoids names collision by appending '.001'
        mesh['jbeam_part'] = part_name
        part_obj = bpy.data.objects.new(part_name, mesh)

        data_buf = StringIO()
        if ctx.listt is not None:
            bm = bmesh.new()

            for section_ctx in ctx.listt.getChildren():
                result = section_ctx.accept(self)
                with Switch(type(result)) as case:
                    if case(IDObject):
                        self.set_parent(result, part_obj)
                    elif case(GeneratorType):
                        result.send(None)  # charge generator
                        # generator returns a placeholder text
                        data_buf.write(result.send(bm))
                        data_buf.write('\n')
                    elif case(str):
                        # other sections
                        data_buf.write(result)
                        data_buf.write('\n')
                    else:
                        raise ValueError("Section not implemented")
            bm.to_mesh(mesh)

        mesh['jbeam_part_data'] = data_buf.getvalue()
        mesh.update()
        return part_obj

    def set_parent(self, obj, parent, prn_type='OBJECT'):
        obj.parent = parent
        obj.parent_type = prn_type
        self.helper_objects.append(obj)
        return obj

    # ============================== slots ==============================

    def visitSection_Slots(self, ctx: jbeamParser.Section_SlotsContext):
        slots_empty = bpy.data.objects.new(ctx.name.text.strip('"'), None)
        # slot section has no transform modifiers
        slots_empty.lock_location = (True, True, True)
        self.lock_rot_scale(slots_empty)
        if ctx.listt is not None:
            self.visitChildren(ctx.listt, slots_empty)
        return slots_empty

    def visitSlot(self, ctx: jbeamParser.SlotContext):
        slot = bpy.data.objects.new(ctx.stype.string_item, None)
        slot["description"] = ctx.description.string_item
        slot["default"] = ctx.default.string_item
        self.lock_rot_scale(slot)

        ctx.slot = slot
        if ctx.prop_list is not None:
            self.visitChildren(ctx.prop_list, slot)
        return slot

    def visitChildren(self, node, aggregator=None):
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
                    self.set_parent(child_result, aggregator)
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

    def visitSection_Nodes(self, ctx: jbeamParser.Section_NodesContext):
        bm = yield  # bmesh
        id_layer = bm.verts.layers.string.new('jbeamNodeId')
        prop_layer = bm.verts.layers.string.new('jbeamNodeProps')
        if ctx.listt is not None:
            self.visitChildren(ctx.listt, (bm, id_layer, prop_layer))
        bm.verts.ensure_lookup_table()
        yield self.get_src_text_replaced(ctx, ctx.listt, '${nodes}')

    def visitNode(self, ctx: jbeamParser.NodeContext):
        bm, id_layer, prop_layer = yield  # receive visitChildren's aggregator kwarg
        vert = bm.verts.new((float(ctx.posX.text), float(ctx.posY.text), float(ctx.posZ.text)))
        _id = ctx.id1.string_item
        vert[id_layer] = _id.encode()  # set node id to the data layer
        self._vertsIndex[_id] = vert
        # node props
        if ctx.props is not None:
            vert[prop_layer] = self.get_src_text_replaced(ctx.props).encode()
        yield vert

    def visitNodeProps(self, ctx: jbeamParser.NodePropsContext):
        # ToDo Node Props
        return None

    # ============================== beams ==============================

    def visitSection_Beams(self, ctx: jbeamParser.Section_BeamsContext):
        bm = yield
        id_layer = bm.verts.layers.string.active
        if id_layer is None:
            # in case if no nodes section, i.e. beams with parent part nodes
            id_layer = bm.verts.layers.string.new('jbeamNodeId')
        beam_layer = bm.edges.layers.int.new('jbeam')
        if ctx.listt is not None:
            self.visitChildren(ctx.listt, (bm, id_layer, beam_layer))
        bm.edges.ensure_lookup_table()
        yield self.get_src_text_replaced(ctx, ctx.listt, '${beams}')

    def visitBeam(self, ctx: jbeamParser.BeamContext):
        bm, id_layer, beam_layer = yield
        id1 = ctx.id1.string_item
        id2 = ctx.id2.string_item
        v1, v2 = self._vertsIndex.get(id1), self._vertsIndex.get(id2)
        # check for attaching to parent
        if not (v1 or v2):
            # both belong to parent? ok
            v1 = self.new_dummy_node(bm, id_layer, id1)
            v2 = self.new_dummy_node(bm, id_layer, id2, v1.co)
        elif not v1:
            # v1 belongs to parent
            v1 = self.new_dummy_node(bm, id_layer, id1, v2.co)
        elif not v2:
            v2 = self.new_dummy_node(bm, id_layer, id2, v1.co)

        try:
            edge = bm.edges.new((v1, v2))  # throws on duplicates
            edge[beam_layer] = 1
            yield edge
        except ValueError as err:
            print(err, id1, id2)  # ToDo handle duplicates
            yield

    def new_dummy_node(self, bm, id_layer, dummy_id: str, co=None):
        """
        Add parent node representation to be able to store attaching beams.
        Adds '~' to the beginning of id, but _vertsIndex keeps original id.
        :param bm: bmesh
        :param id_layer: bmesh.types.BMLayerItem
        :param dummy_id: string
        :param co: mathutils.Vector
        :return: bmesh.types.BMVert
        """
        if co:
            vert = bm.verts.new(co)
            # hang dummy node
            vert.co.z -= .3
        else:
            vert = bm.verts.new((.0, .0, .0))
        vert[id_layer] = ''.join(('~', dummy_id)).encode()
        self._vertsIndex[dummy_id] = vert
        return vert

    def visitBeamProps(self, ctx: jbeamParser.BeamPropsContext):
        return None

    # ============================== collision triangles ==============================

    def visitSection_Coltris(self, ctx: jbeamParser.Section_ColtrisContext):
        bm = yield
        if ctx.listt is not None:
            self.visitChildren(ctx.listt, bm)
        bm.faces.ensure_lookup_table()
        yield self.get_src_text_replaced(ctx, ctx.listt, '${triangles}')

    def visitColtri(self, ctx: jbeamParser.ColtriContext):
        bm = yield
        id1 = ctx.id1.string_item
        id2 = ctx.id2.string_item
        id3 = ctx.id3.string_item
        v_cache = self._vertsIndex
        v1, v2, v3 = v_cache.get(id1), v_cache.get(id2), v_cache.get(id3)
        if v1 and v2 and v3:
            try:
                face = bm.faces.new((v1, v2, v3))
                yield face
            except ValueError as err:
                print(err, id1, id2, id3)  # ToDo handle duplicates
                yield
        else:
            # coltri with parent nodes?? ok
            print('Skipped triangle with parent nodes [{} {} {}]: not implemented')
            yield

    def visitColtriProps(self, ctx: jbeamParser.ColtriPropsContext):
        return None  # ToDo ColtriProps

    # ============================== unknown section ==============================

    def visitSection_Unknown(self, ctx: jbeamParser.Section_UnknownContext):
        # return source text
        src = ctx.parser.getTokenStream().getText(ctx.getSourceInterval())
        # escape for templating
        src = src.replace('$', '$$')
        return src

    def visitSection_Hydros(self, ctx: jbeamParser.Section_HydrosContext):
        return self.visitSection_Unknown(ctx)

    def visitSection_SlotType(self, ctx: jbeamParser.Section_SlotTypeContext):
        return self.visitSection_Unknown(ctx)


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
