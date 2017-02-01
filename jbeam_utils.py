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

    def visitPart(self, ctx: jbeamParser.PartContext):
        print('part: ' + ctx.name.text)
        bm = bmesh.new()  # each part in separate object
        self._bm = bm
        self._idLayer = bm.verts.layers.string.new('jbeamNodeId')

        self.visitChildren(ctx)

        bm.verts.ensure_lookup_table()
        mesh = bpy.data.meshes.new(ctx.name.text.strip('"'))
        bm.to_mesh(mesh)
        mesh.update()
        return mesh

    def aggregateResult(self, aggregate, nextResult):
        if nextResult is None:
            return aggregate

        if aggregate is None:
            aggregate = [nextResult]
        else:
            aggregate.append(nextResult)
        return aggregate

    def visitJNodeObj(self, ctx: jbeamParser.JNodeObjContext):
        print(ctx.getText())
        vert = self._bm.verts.new((float(ctx.posX.text), float(ctx.posY.text), float(ctx.posZ.text)))
        vert[self._idLayer] = ctx.id.text.strip('"').encode()  # set JNode id
        return
