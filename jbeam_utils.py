import sys
import bpy
import bmesh
from antlr4 import *
from .jb.jbeamLexer import jbeamLexer
from .jb.jbeamParser import jbeamParser
from .jb.jbeamVisitor import jbeamVisitor
import pdb


def file_to_meshes(filepath, encoding='utf-8'):
    print('jbeam_utils.file_to_meshes(...): start')

    f_stream = FileStream(filepath, encoding)

    lexer = jbeamLexer(f_stream)
    stream = CommonTokenStream(lexer)
    parser = jbeamParser(stream)
    tree = parser.jbeam()
    # print(tree.getText())
    print('jbeam_utils.file_to_meshes(...): parse tree ok')

    meshList = MeshListBuilder().visit(tree)
    print('jbeam_utils.file_to_meshes(...): meshes ok')
    return meshList


class MeshListBuilder(jbeamVisitor):
    def __init__(self):
        self._bm = None
        self._idLayer = None
        self._vertsCache = None

    def visitPart(self, ctx: jbeamParser.PartContext):
        print('part: ' + ctx.name.text)
        bm = bmesh.new()  # each part in separate object
        self._bm = bm
        self._idLayer = bm.verts.layers.string.new('jbeamNodeId')
        self._vertsCache = {}

        self.visitChildren(ctx)

        bm.verts.ensure_lookup_table()
        mesh = bpy.data.meshes.new(ctx.name.text.strip('"'))
        bm.to_mesh(mesh)
        mesh.update()
        return mesh

    # Aggregates meshes for further visit(...) return
    def aggregateResult(self, aggregate, nextResult):
        if nextResult is None:
            return aggregate

        if aggregate is None:
            aggregate = [nextResult]
        else:
            aggregate.append(nextResult)
        return aggregate

    def visitSecNodes(self, ctx: jbeamParser.SecNodesContext):
        self.visitChildren(ctx)
        self._bm.verts.ensure_lookup_table()

    def visitJNodeObj(self, ctx: jbeamParser.JNodeObjContext):
        vert = self._bm.verts.new((float(ctx.posX.text), float(ctx.posY.text), float(ctx.posZ.text)))
        id = ctx.id.text.strip('"')
        vert[self._idLayer] = id.encode()  # set JNode id
        self._vertsCache[id] = vert
        return

    def visitSecBeams(self, ctx: jbeamParser.SecBeamsContext):
        self.visitChildren(ctx)
        self._bm.edges.ensure_lookup_table()

    def visitBeam(self, ctx: jbeamParser.BeamContext):
        id1 = ctx.id1.text.strip('"')
        id2 = ctx.id2.text.strip('"')
        v1, v2 = self._vertsCache.get(id1), self._vertsCache.get(id2)
        if v1 and v2:
            try:
                self._bm.edges.new((v1, v2))  # throws on duplicates
            except ValueError as err:
                print(err, ' ', id1, ' ', id2)  # ToDo handle duplicates
        # return self.visitChildren(ctx)
