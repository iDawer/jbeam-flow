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
    def visitPart(self, ctx: jbeamParser.PartContext):
        print('part: ' + ctx.name.text)
        self._bm = bmesh.new()  # each part in separate object
        self.visitChildren(ctx)

        self._bm.verts.ensure_lookup_table()
        mesh = bpy.data.meshes.new(str.strip(ctx.name.text, '"'))
        self._bm.to_mesh(mesh)
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
        self._bm.verts.new((float(ctx.posX.text), float(ctx.posY.text), float(ctx.posZ.text)))
        return
