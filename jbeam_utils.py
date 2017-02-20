import bpy
import bmesh

from antlr4 import *  # ToDo: get rid of the global antlr4 lib
from antlr4.TokenStreamRewriter import TokenStreamRewriter
from .jb import jbeamLexer, jbeamParser, jbeamVisitor
from .misc import Triangle


def to_tree(jbeam_data: str):
    data_stream = InputStream(jbeam_data)

    lexer = jbeamLexer(data_stream)
    stream = CommonTokenStream(lexer)
    parser = jbeamParser(stream)
    tree = parser.jbeam()

    return tree


# Aggregator types
JBEAM = 0
PART = 1
SECTION_SLOTS = 2
SECTION_UNKNOWN = 3
SLOT = 4
MAP = 5


class PartObjectsBuilder(jbeamVisitor):
    def __init__(self, name='JBeam file'):
        self.name = name
        self._bm = None
        self._idLayer = None
        self._vertsIndex = None
        self._beamLayer = None
        # self._slots_empty = None
        self._current = None
        self.parts_group = None
        self.helper_objects = []

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
        bm = bmesh.new()  # each part in separate object
        self._bm = bm
        self._idLayer = bm.verts.layers.string.new('jbeamNodeId')
        self._vertsIndex = {}
        self._beamLayer = bm.edges.layers.int.new('jbeam')
        # self._slots_empty = None

        # self.visitChildren(ctx)

        bm.verts.ensure_lookup_table()
        mesh = bpy.data.meshes.new(part_name)
        bm.to_mesh(mesh)
        mesh.update()
        # Save part name explicitly, due Blender avoids names collision by appending '.001'
        mesh['jbeam_part'] = part_name

        part_obj = bpy.data.objects.new(part_name, mesh)

        if ctx.listt is not None:
            for section_ctx in ctx.listt.getChildren():
                if isinstance(section_ctx, jbeamParser.Section_SlotsContext):
                    slots_empty = section_ctx.accept(self)
                    self.set_parent(slots_empty, part_obj)

        return part_obj

    def aggregateResult(self, aggregator, next_result):
        if next_result is None:
            return aggregator

        if isinstance(next_result, tuple):
            raise ValueError("stop")
            # parts aggregator is a Group type
            if next_result[0] == PART:
                if aggregator is None:
                    aggregator = bpy.data.groups.new(self.name)
                aggregator.objects.link(next_result[1])
            elif next_result[0] == SECTION_SLOTS:
                if aggregator is None:
                    # create part object
                    aggregator = bpy.data.objects.new('', bpy.data.meshes.new(''))
                self.set_parent(next_result[1], aggregator)
            elif next_result[0] == SECTION_UNKNOWN:
                if aggregator is None:
                    # part object still has not been created
                    aggregator = bpy.data.objects.new('', bpy.data.meshes.new(''))
                # hmmm, what to do?
                pass
            elif next_result[0] == SLOT:
                if aggregator is None:
                    # create slots container empty
                    aggregator = bpy.data.objects.new('', None)
                self.set_parent(next_result[1], aggregator)
            elif next_result[0] == MAP:
                if aggregator is None:
                    aggregator = {}
                aggregator[next_result[1]] = next_result[2]
            else:
                raise ValueError("Unsupported aggregation")
        else:
            if aggregator is None:
                aggregator = next_result
            # else:  # aggregator and next_result is not None
            #     # aggregate.append(next_result)
            #     raise ValueError("Can't aggregate type " + str(type(next_result)))
        return aggregator

    def set_parent(self, obj, parent, prn_type='OBJECT'):
        obj.parent = parent
        obj.parent_type = prn_type
        self.helper_objects.append(obj)
        return obj

    def shouldVisitNextChild(self, node, currentResult):
        return not isinstance(node, jbeamParser.Section_SlotsContext)

    # def visitSection_Unknown(self, ctx: jbeamParser.Section_UnknownContext):
    #     # force part object create
    #     return SECTION_UNKNOWN,

    # ============================== slots ==============================

    def visitSection_Slots(self, ctx: jbeamParser.Section_SlotsContext):
        slots_empty = bpy.data.objects.new(ctx.name.text.strip('"'), None)
        # slot section has no transform modifiers
        slots_empty.lock_location = (True, True, True)
        self.lock_rot_scale(slots_empty)
        if ctx.listt is not None:
            for slot_ctx in ctx.listt.getChildren():
                slot = slot_ctx.accept(self)
                self.set_parent(slot, slots_empty)
        # self._slots_empty = slots_empty  # > visitPart
        return slots_empty

    def visitSlot(self, ctx: jbeamParser.SlotContext):
        slot = bpy.data.objects.new(ctx.stype.string_item, None)
        slot["description"] = ctx.description.string_item
        slot["default"] = ctx.default.string_item
        self.lock_rot_scale(slot)

        ctx.slot = slot
        if ctx.prop_list is not None:
            for prop_ctx in ctx.prop_list.getChildren():
                if isinstance(prop_ctx, jbeamParser.SlotProp_NodeOffsetContext):
                    slot.location = prop_ctx.node_offset.accept(self)

        return slot  # result goes aggregate > visitSecSlots

    @staticmethod
    def lock_rot_scale(obj):
        obj.lock_rotation = (True, True, True)
        obj.lock_rotation_w = True
        obj.lock_rotations_4d = True
        obj.lock_scale = (True, True, True)

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

    def visitSection_Nodes(self, ctx: jbeamParser.Section_NodesContext):
        self.visitChildren(ctx)
        self._bm.verts.ensure_lookup_table()

    def visitNode(self, ctx: jbeamParser.NodeContext):
        vert = self._bm.verts.new((float(ctx.posX.text), float(ctx.posY.text), float(ctx.posZ.text)))
        _id = ctx.id1.string_item
        vert[self._idLayer] = _id.encode()  # set JNode id
        self._vertsIndex[_id] = vert
        return

    def visitSection_Beams(self, ctx: jbeamParser.Section_BeamsContext):
        self.visitChildren(ctx)
        self._bm.edges.ensure_lookup_table()

    def visitBeam(self, ctx: jbeamParser.BeamContext):
        id1 = ctx.id1.string_item
        id2 = ctx.id2.string_item
        v1, v2 = self._vertsIndex.get(id1), self._vertsIndex.get(id2)
        # check for attaching to parent
        if not (v1 or v2):
            # both belong to parent? ok
            v1 = self.new_dummy_node(id1)
            v2 = self.new_dummy_node(id2, v1.co)
        elif not v1:
            # v1 belongs to parent
            v1 = self.new_dummy_node(id1, v2.co)
        elif not v2:
            v2 = self.new_dummy_node(id2, v1.co)

        try:
            edge = self._bm.edges.new((v1, v2))  # throws on duplicates
            edge[self._beamLayer] = 1
        except ValueError as err:
            print(err, id1, id2)  # ToDo handle duplicates

    def new_dummy_node(self, dummy_id: str, co=None):
        """
        Add parent node representation to be able to store attaching beams.
        Adds '~' to the beginning of id, but _vertsIndex keeps original id.
        :param dummy_id: string
        :param co: mathutils.Vector
        :return: bmesh.types.BMVert
        """
        if co:
            vert = self._bm.verts.new(co)
            # hang dummy node
            vert.co.z -= .3
        else:
            vert = self._bm.verts.new((.0, .0, .0))
        vert[self._idLayer] = ''.join(('~', dummy_id)).encode()
        self._vertsIndex[dummy_id] = vert
        return vert

    def visitColtri(self, ctx: jbeamParser.ColtriContext):
        id1 = ctx.id1.string_item
        id2 = ctx.id2.string_item
        id3 = ctx.id3.string_item
        v_cache = self._vertsIndex
        v1, v2, v3 = v_cache.get(id1), v_cache.get(id2), v_cache.get(id3)
        if v1 and v2 and v3:
            try:
                self._bm.faces.new((v1, v2, v3))
            except ValueError as err:
                print(err, id1, id2, id3)  # ToDo handle duplicates
        else:
            # coltri with parent nodes?? ok
            print('Skipped triangle with parent nodes [{} {} {}]: not implemented')


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
