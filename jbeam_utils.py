import bpy
import bmesh
from antlr4 import *  # ToDo: get rid of the global antlr4 lib
from .jb import jbeamLexer, jbeamParser, jbeamVisitor


def data_to_meshes(data: str):
    data_stream = InputStream(data)

    lexer = jbeamLexer(data_stream)
    stream = CommonTokenStream(lexer)
    parser = jbeamParser(stream)
    tree = parser.jbeam()

    mesh_list = MeshListBuilder().visit(tree)
    return mesh_list


class MeshListBuilder(jbeamVisitor):
    def __init__(self):
        self._bm = None
        self._idLayer = None
        self._vertsCache = None
        self._beamLayer = None

    def visitPart(self, ctx: jbeamParser.PartContext):
        print('part: ' + ctx.name.string_item)
        bm = bmesh.new()  # each part in separate object
        self._bm = bm
        self._idLayer = bm.verts.layers.string.new('jbeamNodeId')
        self._vertsCache = {}
        self._beamLayer = bm.edges.layers.int.new('jbeam')

        self.visitChildren(ctx)

        bm.verts.ensure_lookup_table()
        mesh = bpy.data.meshes.new(ctx.name.string_item)
        bm.to_mesh(mesh)
        mesh.update()
        # Save part name explicitly, due Blender avoids name collision by appending '.001'
        mesh['jbeam_part'] = ctx.name.string_item
        return mesh

    # Aggregates meshes for further visit(...) return
    def aggregateResult(self, aggregate, next_result):
        if next_result is None:
            return aggregate

        if aggregate is None:
            aggregate = [next_result]
        else:
            aggregate.append(next_result)
        return aggregate

    def visitSecNodes(self, ctx: jbeamParser.SecNodesContext):
        self.visitChildren(ctx)
        self._bm.verts.ensure_lookup_table()

    def visitJnode(self, ctx: jbeamParser.JnodeContext):
        vert = self._bm.verts.new((float(ctx.posX.text), float(ctx.posY.text), float(ctx.posZ.text)))
        _id = ctx.id1.string_item
        vert[self._idLayer] = _id.encode()  # set JNode id
        self._vertsCache[_id] = vert
        return

    def visitSecBeams(self, ctx: jbeamParser.SecBeamsContext):
        self.visitChildren(ctx)
        self._bm.edges.ensure_lookup_table()

    def visitBeam(self, ctx: jbeamParser.BeamContext):
        id1 = ctx.id1.string_item
        id2 = ctx.id2.string_item
        v1, v2 = self._vertsCache.get(id1), self._vertsCache.get(id2)
        if v1 and v2:
            try:
                edge = self._bm.edges.new((v1, v2))  # throws on duplicates
                edge[self._beamLayer] = 1
            except ValueError as err:
                print(err, ' ', id1, ' ', id2)  # ToDo handle duplicates

    def visitColtri(self, ctx: jbeamParser.ColtriContext):
        id1 = ctx.id1.string_item
        id2 = ctx.id2.string_item
        id3 = ctx.id3.string_item
        v_cache = self._vertsCache
        v1, v2, v3 = v_cache.get(id1), v_cache.get(id2), v_cache.get(id3)
        if v1 and v2 and v3:
            try:
                self._bm.faces.new((v1, v2, v3))
            except ValueError as err:
                print(err, ' ', id1, ' ', id2, ' ', id3)  # ToDo handle duplicates


class NodeCollector(jbeamVisitor):
    def __init__(self, part_name: str):
        super().__init__()
        self.part_name = part_name
        self.nodes = {}

    def visitPart(self, ctx: jbeamParser.PartContext):
        if ctx.name.string_item == self.part_name:
            return self.visitChildren(ctx)

    def visitJnode(self, node_ctx: jbeamParser.JnodeContext):
        self.nodes[node_ctx.id1.string_item] = node_ctx


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


