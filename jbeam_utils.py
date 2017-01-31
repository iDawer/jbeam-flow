import sys
import bpy
from antlr4 import *
from .jb.jbeamLexer import jbeamLexer
from .jb.jbeamParser import jbeamParser
from .jb.jbeamVisitor import jbeamVisitor
import pdb


def read_some_data(context, filepath, use_some_setting):
    print("running read_some_data...")

    f_stream = FileStream(filepath, 'utf-8')
    print(f_stream.strdata)

    lexer = jbeamLexer(f_stream)
    stream = CommonTokenStream(lexer)
    parser = jbeamParser(stream)
    tree = parser.jbeam()
    print(tree.getText())
    print('finished 4')

    return {'FINISHED'}
