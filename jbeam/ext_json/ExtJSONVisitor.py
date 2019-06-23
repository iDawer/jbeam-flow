# Generated from C:/Users/Dawer/Documents/ANTLR playground\ExtJSON.g4 by ANTLR 4.6
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ExtJSONParser import ExtJSONParser
else:
    from ExtJSONParser import ExtJSONParser

# This class defines a complete generic visitor for a parse tree produced by ExtJSONParser.

class ExtJSONVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ExtJSONParser#json.
    def visitJson(self, ctx:ExtJSONParser.JsonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExtJSONParser#object.
    def visitObject(self, ctx:ExtJSONParser.ObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExtJSONParser#pairs.
    def visitPairs(self, ctx:ExtJSONParser.PairsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExtJSONParser#pair.
    def visitPair(self, ctx:ExtJSONParser.PairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExtJSONParser#array.
    def visitArray(self, ctx:ExtJSONParser.ArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExtJSONParser#values.
    def visitValues(self, ctx:ExtJSONParser.ValuesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExtJSONParser#ValueString.
    def visitValueString(self, ctx:ExtJSONParser.ValueStringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExtJSONParser#ValueAtom.
    def visitValueAtom(self, ctx:ExtJSONParser.ValueAtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExtJSONParser#ValueObject.
    def visitValueObject(self, ctx:ExtJSONParser.ValueObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ExtJSONParser#ValueArray.
    def visitValueArray(self, ctx:ExtJSONParser.ValueArrayContext):
        return self.visitChildren(ctx)



del ExtJSONParser