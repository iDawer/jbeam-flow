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


    # Visit a parse tree produced by jbeamParser#partSeq.
    def visitPartSeq(self, ctx:jbeamParser.PartSeqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#part.
    def visitPart(self, ctx:jbeamParser.PartContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#sectionSeq.
    def visitSectionSeq(self, ctx:jbeamParser.SectionSeqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Section_SlotType.
    def visitSection_SlotType(self, ctx:jbeamParser.Section_SlotTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Section_Slots.
    def visitSection_Slots(self, ctx:jbeamParser.Section_SlotsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Section_Nodes.
    def visitSection_Nodes(self, ctx:jbeamParser.Section_NodesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Section_Beams.
    def visitSection_Beams(self, ctx:jbeamParser.Section_BeamsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Section_Hydros.
    def visitSection_Hydros(self, ctx:jbeamParser.Section_HydrosContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Section_Coltris.
    def visitSection_Coltris(self, ctx:jbeamParser.Section_ColtrisContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Section_Unknown.
    def visitSection_Unknown(self, ctx:jbeamParser.Section_UnknownContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#slotSeq.
    def visitSlotSeq(self, ctx:jbeamParser.SlotSeqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#slot.
    def visitSlot(self, ctx:jbeamParser.SlotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#slotPropSeq.
    def visitSlotPropSeq(self, ctx:jbeamParser.SlotPropSeqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#SlotProp_NodeOffset.
    def visitSlotProp_NodeOffset(self, ctx:jbeamParser.SlotProp_NodeOffsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#SlotProp_CoreSlot.
    def visitSlotProp_CoreSlot(self, ctx:jbeamParser.SlotProp_CoreSlotContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#SlotProp_Unknown.
    def visitSlotProp_Unknown(self, ctx:jbeamParser.SlotProp_UnknownContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#offset.
    def visitOffset(self, ctx:jbeamParser.OffsetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#OffsetAxisX.
    def visitOffsetAxisX(self, ctx:jbeamParser.OffsetAxisXContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#OffsetAxisY.
    def visitOffsetAxisY(self, ctx:jbeamParser.OffsetAxisYContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#OffsetAxisZ.
    def visitOffsetAxisZ(self, ctx:jbeamParser.OffsetAxisZContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#nodeSeq.
    def visitNodeSeq(self, ctx:jbeamParser.NodeSeqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Node.
    def visitNode(self, ctx:jbeamParser.NodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProps.
    def visitNodeProps(self, ctx:jbeamParser.NodePropsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#nodePropObj.
    def visitNodePropObj(self, ctx:jbeamParser.NodePropObjContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProp_NodeWeight.
    def visitNodeProp_NodeWeight(self, ctx:jbeamParser.NodeProp_NodeWeightContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProp_SelfCollision.
    def visitNodeProp_SelfCollision(self, ctx:jbeamParser.NodeProp_SelfCollisionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProp_Collision.
    def visitNodeProp_Collision(self, ctx:jbeamParser.NodeProp_CollisionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProp_Group.
    def visitNodeProp_Group(self, ctx:jbeamParser.NodeProp_GroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProp_FrictionCoef.
    def visitNodeProp_FrictionCoef(self, ctx:jbeamParser.NodeProp_FrictionCoefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProp_NodeMaterial.
    def visitNodeProp_NodeMaterial(self, ctx:jbeamParser.NodeProp_NodeMaterialContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProp_Fixed.
    def visitNodeProp_Fixed(self, ctx:jbeamParser.NodeProp_FixedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProp_SurfaceCoef.
    def visitNodeProp_SurfaceCoef(self, ctx:jbeamParser.NodeProp_SurfaceCoefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProp_VolumeCoef.
    def visitNodeProp_VolumeCoef(self, ctx:jbeamParser.NodeProp_VolumeCoefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeProp_Unknown.
    def visitNodeProp_Unknown(self, ctx:jbeamParser.NodeProp_UnknownContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeGroupProp_SingleGroup.
    def visitNodeGroupProp_SingleGroup(self, ctx:jbeamParser.NodeGroupProp_SingleGroupContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#NodeGroupProp_Groups.
    def visitNodeGroupProp_Groups(self, ctx:jbeamParser.NodeGroupProp_GroupsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#beamSeq.
    def visitBeamSeq(self, ctx:jbeamParser.BeamSeqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Beam.
    def visitBeam(self, ctx:jbeamParser.BeamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#BeamProps.
    def visitBeamProps(self, ctx:jbeamParser.BeamPropsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#coltriSeq.
    def visitColtriSeq(self, ctx:jbeamParser.ColtriSeqContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#Coltri.
    def visitColtri(self, ctx:jbeamParser.ColtriContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#ColtriProps.
    def visitColtriProps(self, ctx:jbeamParser.ColtriPropsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#tableHeader.
    def visitTableHeader(self, ctx:jbeamParser.TableHeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#genericStringSeq.
    def visitGenericStringSeq(self, ctx:jbeamParser.GenericStringSeqContext):
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


    # Visit a parse tree produced by jbeamParser#boolean.
    def visitBoolean(self, ctx:jbeamParser.BooleanContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by jbeamParser#genericString.
    def visitGenericString(self, ctx:jbeamParser.GenericStringContext):
        return self.visitChildren(ctx)



del jbeamParser