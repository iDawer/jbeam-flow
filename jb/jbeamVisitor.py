# Generated from C:/Users/Dawer/Documents/ANTLR playground\jbeam.g4 by ANTLR 4.6
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .jbeamParser import jbeamParser
else:
    from jbeamParser import jbeamParser

# This class defines a complete generic visitor for a parse tree produced by jbeamParser.

class jbeamVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by jbeamParser#jbeam.
    def visitJbeam(self, ctx:jbeamParser.JbeamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#part.
    def visitPart(self, ctx:jbeamParser.PartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#partObj.
    def visitPartObj(self, ctx:jbeamParser.PartObjContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#SecNodes.
    def visitSecNodes(self, ctx:jbeamParser.SecNodesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#SecBeams.
    def visitSecBeams(self, ctx:jbeamParser.SecBeamsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#SecColtris.
    def visitSecColtris(self, ctx:jbeamParser.SecColtrisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#SecUnknown.
    def visitSecUnknown(self, ctx:jbeamParser.SecUnknownContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#arrayOfJnodes.
    def visitArrayOfJnodes(self, ctx:jbeamParser.ArrayOfJnodesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#jnode.
    def visitJnode(self, ctx:jbeamParser.JnodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#jnodeProps.
    def visitJnodeProps(self, ctx:jbeamParser.JnodePropsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#PropNodeWeight.
    def visitPropNodeWeight(self, ctx:jbeamParser.PropNodeWeightContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#PropSelfCollision.
    def visitPropSelfCollision(self, ctx:jbeamParser.PropSelfCollisionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#PropCollision.
    def visitPropCollision(self, ctx:jbeamParser.PropCollisionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#PropGroup.
    def visitPropGroup(self, ctx:jbeamParser.PropGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#PropFrictionCoef.
    def visitPropFrictionCoef(self, ctx:jbeamParser.PropFrictionCoefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#PropNodeMaterial.
    def visitPropNodeMaterial(self, ctx:jbeamParser.PropNodeMaterialContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#PropFixed.
    def visitPropFixed(self, ctx:jbeamParser.PropFixedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#PropSurfaceCoef.
    def visitPropSurfaceCoef(self, ctx:jbeamParser.PropSurfaceCoefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#PropVolumeCoef.
    def visitPropVolumeCoef(self, ctx:jbeamParser.PropVolumeCoefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#PropUnknown.
    def visitPropUnknown(self, ctx:jbeamParser.PropUnknownContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#arrayOfBeams.
    def visitArrayOfBeams(self, ctx:jbeamParser.ArrayOfBeamsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#tableHeader.
    def visitTableHeader(self, ctx:jbeamParser.TableHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#beam.
    def visitBeam(self, ctx:jbeamParser.BeamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#beamProps.
    def visitBeamProps(self, ctx:jbeamParser.BeamPropsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#arrayOfColtris.
    def visitArrayOfColtris(self, ctx:jbeamParser.ArrayOfColtrisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#coltri.
    def visitColtri(self, ctx:jbeamParser.ColtriContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#coltriProps.
    def visitColtriProps(self, ctx:jbeamParser.ColtriPropsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#obj.
    def visitObj(self, ctx:jbeamParser.ObjContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#array.
    def visitArray(self, ctx:jbeamParser.ArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#keyVal.
    def visitKeyVal(self, ctx:jbeamParser.KeyValContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#String.
    def visitString(self, ctx:jbeamParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Atom.
    def visitAtom(self, ctx:jbeamParser.AtomContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#ObjectValue.
    def visitObjectValue(self, ctx:jbeamParser.ObjectValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#ArrayValue.
    def visitArrayValue(self, ctx:jbeamParser.ArrayValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#TrueVal.
    def visitTrueVal(self, ctx:jbeamParser.TrueValContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#FalseVal.
    def visitFalseVal(self, ctx:jbeamParser.FalseValContext):
        return self.visitChildren(ctx)



del jbeamParser