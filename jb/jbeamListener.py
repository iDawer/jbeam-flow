# Generated from C:/Users/Dawer/Documents/ANTLR playground\jbeam.g4 by ANTLR 4.6
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .jbeamParser import jbeamParser
else:
    from jbeamParser import jbeamParser

# This class defines a complete listener for a parse tree produced by jbeamParser.
class jbeamListener(ParseTreeListener):

    # Enter a parse tree produced by jbeamParser#jbeam.
    def enterJbeam(self, ctx:jbeamParser.JbeamContext):
        pass

    # Exit a parse tree produced by jbeamParser#jbeam.
    def exitJbeam(self, ctx:jbeamParser.JbeamContext):
        pass


    # Enter a parse tree produced by jbeamParser#part.
    def enterPart(self, ctx:jbeamParser.PartContext):
        pass

    # Exit a parse tree produced by jbeamParser#part.
    def exitPart(self, ctx:jbeamParser.PartContext):
        pass


    # Enter a parse tree produced by jbeamParser#partObj.
    def enterPartObj(self, ctx:jbeamParser.PartObjContext):
        pass

    # Exit a parse tree produced by jbeamParser#partObj.
    def exitPartObj(self, ctx:jbeamParser.PartObjContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodesObj.
    def enterNodesObj(self, ctx:jbeamParser.NodesObjContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodesObj.
    def exitNodesObj(self, ctx:jbeamParser.NodesObjContext):
        pass


    # Enter a parse tree produced by jbeamParser#UnknownSection.
    def enterUnknownSection(self, ctx:jbeamParser.UnknownSectionContext):
        pass

    # Exit a parse tree produced by jbeamParser#UnknownSection.
    def exitUnknownSection(self, ctx:jbeamParser.UnknownSectionContext):
        pass


    # Enter a parse tree produced by jbeamParser#arrayOfJnodes.
    def enterArrayOfJnodes(self, ctx:jbeamParser.ArrayOfJnodesContext):
        pass

    # Exit a parse tree produced by jbeamParser#arrayOfJnodes.
    def exitArrayOfJnodes(self, ctx:jbeamParser.ArrayOfJnodesContext):
        pass


    # Enter a parse tree produced by jbeamParser#JNodesTableHeader.
    def enterJNodesTableHeader(self, ctx:jbeamParser.JNodesTableHeaderContext):
        pass

    # Exit a parse tree produced by jbeamParser#JNodesTableHeader.
    def exitJNodesTableHeader(self, ctx:jbeamParser.JNodesTableHeaderContext):
        pass


    # Enter a parse tree produced by jbeamParser#JNodeObj.
    def enterJNodeObj(self, ctx:jbeamParser.JNodeObjContext):
        pass

    # Exit a parse tree produced by jbeamParser#JNodeObj.
    def exitJNodeObj(self, ctx:jbeamParser.JNodeObjContext):
        pass


    # Enter a parse tree produced by jbeamParser#JnodeSharedProps.
    def enterJnodeSharedProps(self, ctx:jbeamParser.JnodeSharedPropsContext):
        pass

    # Exit a parse tree produced by jbeamParser#JnodeSharedProps.
    def exitJnodeSharedProps(self, ctx:jbeamParser.JnodeSharedPropsContext):
        pass


    # Enter a parse tree produced by jbeamParser#jnodeProps.
    def enterJnodeProps(self, ctx:jbeamParser.JnodePropsContext):
        pass

    # Exit a parse tree produced by jbeamParser#jnodeProps.
    def exitJnodeProps(self, ctx:jbeamParser.JnodePropsContext):
        pass


    # Enter a parse tree produced by jbeamParser#PropNodeWeight.
    def enterPropNodeWeight(self, ctx:jbeamParser.PropNodeWeightContext):
        pass

    # Exit a parse tree produced by jbeamParser#PropNodeWeight.
    def exitPropNodeWeight(self, ctx:jbeamParser.PropNodeWeightContext):
        pass


    # Enter a parse tree produced by jbeamParser#PropSelfCollision.
    def enterPropSelfCollision(self, ctx:jbeamParser.PropSelfCollisionContext):
        pass

    # Exit a parse tree produced by jbeamParser#PropSelfCollision.
    def exitPropSelfCollision(self, ctx:jbeamParser.PropSelfCollisionContext):
        pass


    # Enter a parse tree produced by jbeamParser#PropCollision.
    def enterPropCollision(self, ctx:jbeamParser.PropCollisionContext):
        pass

    # Exit a parse tree produced by jbeamParser#PropCollision.
    def exitPropCollision(self, ctx:jbeamParser.PropCollisionContext):
        pass


    # Enter a parse tree produced by jbeamParser#PropGroup.
    def enterPropGroup(self, ctx:jbeamParser.PropGroupContext):
        pass

    # Exit a parse tree produced by jbeamParser#PropGroup.
    def exitPropGroup(self, ctx:jbeamParser.PropGroupContext):
        pass


    # Enter a parse tree produced by jbeamParser#PropFrictionCoef.
    def enterPropFrictionCoef(self, ctx:jbeamParser.PropFrictionCoefContext):
        pass

    # Exit a parse tree produced by jbeamParser#PropFrictionCoef.
    def exitPropFrictionCoef(self, ctx:jbeamParser.PropFrictionCoefContext):
        pass


    # Enter a parse tree produced by jbeamParser#PropNodeMaterial.
    def enterPropNodeMaterial(self, ctx:jbeamParser.PropNodeMaterialContext):
        pass

    # Exit a parse tree produced by jbeamParser#PropNodeMaterial.
    def exitPropNodeMaterial(self, ctx:jbeamParser.PropNodeMaterialContext):
        pass


    # Enter a parse tree produced by jbeamParser#PropFixed.
    def enterPropFixed(self, ctx:jbeamParser.PropFixedContext):
        pass

    # Exit a parse tree produced by jbeamParser#PropFixed.
    def exitPropFixed(self, ctx:jbeamParser.PropFixedContext):
        pass


    # Enter a parse tree produced by jbeamParser#PropSurfaceCoef.
    def enterPropSurfaceCoef(self, ctx:jbeamParser.PropSurfaceCoefContext):
        pass

    # Exit a parse tree produced by jbeamParser#PropSurfaceCoef.
    def exitPropSurfaceCoef(self, ctx:jbeamParser.PropSurfaceCoefContext):
        pass


    # Enter a parse tree produced by jbeamParser#PropVolumeCoef.
    def enterPropVolumeCoef(self, ctx:jbeamParser.PropVolumeCoefContext):
        pass

    # Exit a parse tree produced by jbeamParser#PropVolumeCoef.
    def exitPropVolumeCoef(self, ctx:jbeamParser.PropVolumeCoefContext):
        pass


    # Enter a parse tree produced by jbeamParser#PropUnknown.
    def enterPropUnknown(self, ctx:jbeamParser.PropUnknownContext):
        pass

    # Exit a parse tree produced by jbeamParser#PropUnknown.
    def exitPropUnknown(self, ctx:jbeamParser.PropUnknownContext):
        pass


    # Enter a parse tree produced by jbeamParser#obj.
    def enterObj(self, ctx:jbeamParser.ObjContext):
        pass

    # Exit a parse tree produced by jbeamParser#obj.
    def exitObj(self, ctx:jbeamParser.ObjContext):
        pass


    # Enter a parse tree produced by jbeamParser#array.
    def enterArray(self, ctx:jbeamParser.ArrayContext):
        pass

    # Exit a parse tree produced by jbeamParser#array.
    def exitArray(self, ctx:jbeamParser.ArrayContext):
        pass


    # Enter a parse tree produced by jbeamParser#keyVal.
    def enterKeyVal(self, ctx:jbeamParser.KeyValContext):
        pass

    # Exit a parse tree produced by jbeamParser#keyVal.
    def exitKeyVal(self, ctx:jbeamParser.KeyValContext):
        pass


    # Enter a parse tree produced by jbeamParser#String.
    def enterString(self, ctx:jbeamParser.StringContext):
        pass

    # Exit a parse tree produced by jbeamParser#String.
    def exitString(self, ctx:jbeamParser.StringContext):
        pass


    # Enter a parse tree produced by jbeamParser#Atom.
    def enterAtom(self, ctx:jbeamParser.AtomContext):
        pass

    # Exit a parse tree produced by jbeamParser#Atom.
    def exitAtom(self, ctx:jbeamParser.AtomContext):
        pass


    # Enter a parse tree produced by jbeamParser#ObjectValue.
    def enterObjectValue(self, ctx:jbeamParser.ObjectValueContext):
        pass

    # Exit a parse tree produced by jbeamParser#ObjectValue.
    def exitObjectValue(self, ctx:jbeamParser.ObjectValueContext):
        pass


    # Enter a parse tree produced by jbeamParser#ArrayValue.
    def enterArrayValue(self, ctx:jbeamParser.ArrayValueContext):
        pass

    # Exit a parse tree produced by jbeamParser#ArrayValue.
    def exitArrayValue(self, ctx:jbeamParser.ArrayValueContext):
        pass


    # Enter a parse tree produced by jbeamParser#TrueVal.
    def enterTrueVal(self, ctx:jbeamParser.TrueValContext):
        pass

    # Exit a parse tree produced by jbeamParser#TrueVal.
    def exitTrueVal(self, ctx:jbeamParser.TrueValContext):
        pass


    # Enter a parse tree produced by jbeamParser#FalseVal.
    def enterFalseVal(self, ctx:jbeamParser.FalseValContext):
        pass

    # Exit a parse tree produced by jbeamParser#FalseVal.
    def exitFalseVal(self, ctx:jbeamParser.FalseValContext):
        pass


