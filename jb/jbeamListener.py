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


    # Enter a parse tree produced by jbeamParser#partSeq.
    def enterPartSeq(self, ctx:jbeamParser.PartSeqContext):
        pass

    # Exit a parse tree produced by jbeamParser#partSeq.
    def exitPartSeq(self, ctx:jbeamParser.PartSeqContext):
        pass


    # Enter a parse tree produced by jbeamParser#part.
    def enterPart(self, ctx:jbeamParser.PartContext):
        pass

    # Exit a parse tree produced by jbeamParser#part.
    def exitPart(self, ctx:jbeamParser.PartContext):
        pass


    # Enter a parse tree produced by jbeamParser#sectionSeq.
    def enterSectionSeq(self, ctx:jbeamParser.SectionSeqContext):
        pass

    # Exit a parse tree produced by jbeamParser#sectionSeq.
    def exitSectionSeq(self, ctx:jbeamParser.SectionSeqContext):
        pass


    # Enter a parse tree produced by jbeamParser#Section_SlotType.
    def enterSection_SlotType(self, ctx:jbeamParser.Section_SlotTypeContext):
        pass

    # Exit a parse tree produced by jbeamParser#Section_SlotType.
    def exitSection_SlotType(self, ctx:jbeamParser.Section_SlotTypeContext):
        pass


    # Enter a parse tree produced by jbeamParser#Section_Slots.
    def enterSection_Slots(self, ctx:jbeamParser.Section_SlotsContext):
        pass

    # Exit a parse tree produced by jbeamParser#Section_Slots.
    def exitSection_Slots(self, ctx:jbeamParser.Section_SlotsContext):
        pass


    # Enter a parse tree produced by jbeamParser#Section_Nodes.
    def enterSection_Nodes(self, ctx:jbeamParser.Section_NodesContext):
        pass

    # Exit a parse tree produced by jbeamParser#Section_Nodes.
    def exitSection_Nodes(self, ctx:jbeamParser.Section_NodesContext):
        pass


    # Enter a parse tree produced by jbeamParser#Section_Beams.
    def enterSection_Beams(self, ctx:jbeamParser.Section_BeamsContext):
        pass

    # Exit a parse tree produced by jbeamParser#Section_Beams.
    def exitSection_Beams(self, ctx:jbeamParser.Section_BeamsContext):
        pass


    # Enter a parse tree produced by jbeamParser#Section_Hydros.
    def enterSection_Hydros(self, ctx:jbeamParser.Section_HydrosContext):
        pass

    # Exit a parse tree produced by jbeamParser#Section_Hydros.
    def exitSection_Hydros(self, ctx:jbeamParser.Section_HydrosContext):
        pass


    # Enter a parse tree produced by jbeamParser#Section_Coltris.
    def enterSection_Coltris(self, ctx:jbeamParser.Section_ColtrisContext):
        pass

    # Exit a parse tree produced by jbeamParser#Section_Coltris.
    def exitSection_Coltris(self, ctx:jbeamParser.Section_ColtrisContext):
        pass


    # Enter a parse tree produced by jbeamParser#Section_Unknown.
    def enterSection_Unknown(self, ctx:jbeamParser.Section_UnknownContext):
        pass

    # Exit a parse tree produced by jbeamParser#Section_Unknown.
    def exitSection_Unknown(self, ctx:jbeamParser.Section_UnknownContext):
        pass


    # Enter a parse tree produced by jbeamParser#slotSeq.
    def enterSlotSeq(self, ctx:jbeamParser.SlotSeqContext):
        pass

    # Exit a parse tree produced by jbeamParser#slotSeq.
    def exitSlotSeq(self, ctx:jbeamParser.SlotSeqContext):
        pass


    # Enter a parse tree produced by jbeamParser#slot.
    def enterSlot(self, ctx:jbeamParser.SlotContext):
        pass

    # Exit a parse tree produced by jbeamParser#slot.
    def exitSlot(self, ctx:jbeamParser.SlotContext):
        pass


    # Enter a parse tree produced by jbeamParser#slotPropSeq.
    def enterSlotPropSeq(self, ctx:jbeamParser.SlotPropSeqContext):
        pass

    # Exit a parse tree produced by jbeamParser#slotPropSeq.
    def exitSlotPropSeq(self, ctx:jbeamParser.SlotPropSeqContext):
        pass


    # Enter a parse tree produced by jbeamParser#SlotProp_NodeOffset.
    def enterSlotProp_NodeOffset(self, ctx:jbeamParser.SlotProp_NodeOffsetContext):
        pass

    # Exit a parse tree produced by jbeamParser#SlotProp_NodeOffset.
    def exitSlotProp_NodeOffset(self, ctx:jbeamParser.SlotProp_NodeOffsetContext):
        pass


    # Enter a parse tree produced by jbeamParser#SlotProp_CoreSlot.
    def enterSlotProp_CoreSlot(self, ctx:jbeamParser.SlotProp_CoreSlotContext):
        pass

    # Exit a parse tree produced by jbeamParser#SlotProp_CoreSlot.
    def exitSlotProp_CoreSlot(self, ctx:jbeamParser.SlotProp_CoreSlotContext):
        pass


    # Enter a parse tree produced by jbeamParser#SlotProp_Unknown.
    def enterSlotProp_Unknown(self, ctx:jbeamParser.SlotProp_UnknownContext):
        pass

    # Exit a parse tree produced by jbeamParser#SlotProp_Unknown.
    def exitSlotProp_Unknown(self, ctx:jbeamParser.SlotProp_UnknownContext):
        pass


    # Enter a parse tree produced by jbeamParser#offset.
    def enterOffset(self, ctx:jbeamParser.OffsetContext):
        pass

    # Exit a parse tree produced by jbeamParser#offset.
    def exitOffset(self, ctx:jbeamParser.OffsetContext):
        pass


    # Enter a parse tree produced by jbeamParser#OffsetAxisX.
    def enterOffsetAxisX(self, ctx:jbeamParser.OffsetAxisXContext):
        pass

    # Exit a parse tree produced by jbeamParser#OffsetAxisX.
    def exitOffsetAxisX(self, ctx:jbeamParser.OffsetAxisXContext):
        pass


    # Enter a parse tree produced by jbeamParser#OffsetAxisY.
    def enterOffsetAxisY(self, ctx:jbeamParser.OffsetAxisYContext):
        pass

    # Exit a parse tree produced by jbeamParser#OffsetAxisY.
    def exitOffsetAxisY(self, ctx:jbeamParser.OffsetAxisYContext):
        pass


    # Enter a parse tree produced by jbeamParser#OffsetAxisZ.
    def enterOffsetAxisZ(self, ctx:jbeamParser.OffsetAxisZContext):
        pass

    # Exit a parse tree produced by jbeamParser#OffsetAxisZ.
    def exitOffsetAxisZ(self, ctx:jbeamParser.OffsetAxisZContext):
        pass


    # Enter a parse tree produced by jbeamParser#nodeSeq.
    def enterNodeSeq(self, ctx:jbeamParser.NodeSeqContext):
        pass

    # Exit a parse tree produced by jbeamParser#nodeSeq.
    def exitNodeSeq(self, ctx:jbeamParser.NodeSeqContext):
        pass


    # Enter a parse tree produced by jbeamParser#Node.
    def enterNode(self, ctx:jbeamParser.NodeContext):
        pass

    # Exit a parse tree produced by jbeamParser#Node.
    def exitNode(self, ctx:jbeamParser.NodeContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProps.
    def enterNodeProps(self, ctx:jbeamParser.NodePropsContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProps.
    def exitNodeProps(self, ctx:jbeamParser.NodePropsContext):
        pass


    # Enter a parse tree produced by jbeamParser#nodePropSeq.
    def enterNodePropSeq(self, ctx:jbeamParser.NodePropSeqContext):
        pass

    # Exit a parse tree produced by jbeamParser#nodePropSeq.
    def exitNodePropSeq(self, ctx:jbeamParser.NodePropSeqContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProp_NodeWeight.
    def enterNodeProp_NodeWeight(self, ctx:jbeamParser.NodeProp_NodeWeightContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProp_NodeWeight.
    def exitNodeProp_NodeWeight(self, ctx:jbeamParser.NodeProp_NodeWeightContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProp_SelfCollision.
    def enterNodeProp_SelfCollision(self, ctx:jbeamParser.NodeProp_SelfCollisionContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProp_SelfCollision.
    def exitNodeProp_SelfCollision(self, ctx:jbeamParser.NodeProp_SelfCollisionContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProp_Collision.
    def enterNodeProp_Collision(self, ctx:jbeamParser.NodeProp_CollisionContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProp_Collision.
    def exitNodeProp_Collision(self, ctx:jbeamParser.NodeProp_CollisionContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProp_Group.
    def enterNodeProp_Group(self, ctx:jbeamParser.NodeProp_GroupContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProp_Group.
    def exitNodeProp_Group(self, ctx:jbeamParser.NodeProp_GroupContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProp_FrictionCoef.
    def enterNodeProp_FrictionCoef(self, ctx:jbeamParser.NodeProp_FrictionCoefContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProp_FrictionCoef.
    def exitNodeProp_FrictionCoef(self, ctx:jbeamParser.NodeProp_FrictionCoefContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProp_NodeMaterial.
    def enterNodeProp_NodeMaterial(self, ctx:jbeamParser.NodeProp_NodeMaterialContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProp_NodeMaterial.
    def exitNodeProp_NodeMaterial(self, ctx:jbeamParser.NodeProp_NodeMaterialContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProp_Fixed.
    def enterNodeProp_Fixed(self, ctx:jbeamParser.NodeProp_FixedContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProp_Fixed.
    def exitNodeProp_Fixed(self, ctx:jbeamParser.NodeProp_FixedContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProp_SurfaceCoef.
    def enterNodeProp_SurfaceCoef(self, ctx:jbeamParser.NodeProp_SurfaceCoefContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProp_SurfaceCoef.
    def exitNodeProp_SurfaceCoef(self, ctx:jbeamParser.NodeProp_SurfaceCoefContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProp_VolumeCoef.
    def enterNodeProp_VolumeCoef(self, ctx:jbeamParser.NodeProp_VolumeCoefContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProp_VolumeCoef.
    def exitNodeProp_VolumeCoef(self, ctx:jbeamParser.NodeProp_VolumeCoefContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeProp_Unknown.
    def enterNodeProp_Unknown(self, ctx:jbeamParser.NodeProp_UnknownContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeProp_Unknown.
    def exitNodeProp_Unknown(self, ctx:jbeamParser.NodeProp_UnknownContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeGroupProp_SingleGroup.
    def enterNodeGroupProp_SingleGroup(self, ctx:jbeamParser.NodeGroupProp_SingleGroupContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeGroupProp_SingleGroup.
    def exitNodeGroupProp_SingleGroup(self, ctx:jbeamParser.NodeGroupProp_SingleGroupContext):
        pass


    # Enter a parse tree produced by jbeamParser#NodeGroupProp_Groups.
    def enterNodeGroupProp_Groups(self, ctx:jbeamParser.NodeGroupProp_GroupsContext):
        pass

    # Exit a parse tree produced by jbeamParser#NodeGroupProp_Groups.
    def exitNodeGroupProp_Groups(self, ctx:jbeamParser.NodeGroupProp_GroupsContext):
        pass


    # Enter a parse tree produced by jbeamParser#beamSeq.
    def enterBeamSeq(self, ctx:jbeamParser.BeamSeqContext):
        pass

    # Exit a parse tree produced by jbeamParser#beamSeq.
    def exitBeamSeq(self, ctx:jbeamParser.BeamSeqContext):
        pass


    # Enter a parse tree produced by jbeamParser#Beam.
    def enterBeam(self, ctx:jbeamParser.BeamContext):
        pass

    # Exit a parse tree produced by jbeamParser#Beam.
    def exitBeam(self, ctx:jbeamParser.BeamContext):
        pass


    # Enter a parse tree produced by jbeamParser#BeamProps.
    def enterBeamProps(self, ctx:jbeamParser.BeamPropsContext):
        pass

    # Exit a parse tree produced by jbeamParser#BeamProps.
    def exitBeamProps(self, ctx:jbeamParser.BeamPropsContext):
        pass


    # Enter a parse tree produced by jbeamParser#coltriSeq.
    def enterColtriSeq(self, ctx:jbeamParser.ColtriSeqContext):
        pass

    # Exit a parse tree produced by jbeamParser#coltriSeq.
    def exitColtriSeq(self, ctx:jbeamParser.ColtriSeqContext):
        pass


    # Enter a parse tree produced by jbeamParser#Coltri.
    def enterColtri(self, ctx:jbeamParser.ColtriContext):
        pass

    # Exit a parse tree produced by jbeamParser#Coltri.
    def exitColtri(self, ctx:jbeamParser.ColtriContext):
        pass


    # Enter a parse tree produced by jbeamParser#ColtriProps.
    def enterColtriProps(self, ctx:jbeamParser.ColtriPropsContext):
        pass

    # Exit a parse tree produced by jbeamParser#ColtriProps.
    def exitColtriProps(self, ctx:jbeamParser.ColtriPropsContext):
        pass


    # Enter a parse tree produced by jbeamParser#tableHeader.
    def enterTableHeader(self, ctx:jbeamParser.TableHeaderContext):
        pass

    # Exit a parse tree produced by jbeamParser#tableHeader.
    def exitTableHeader(self, ctx:jbeamParser.TableHeaderContext):
        pass


    # Enter a parse tree produced by jbeamParser#genericStringSeq.
    def enterGenericStringSeq(self, ctx:jbeamParser.GenericStringSeqContext):
        pass

    # Exit a parse tree produced by jbeamParser#genericStringSeq.
    def exitGenericStringSeq(self, ctx:jbeamParser.GenericStringSeqContext):
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


    # Enter a parse tree produced by jbeamParser#boolean.
    def enterBoolean(self, ctx:jbeamParser.BooleanContext):
        pass

    # Exit a parse tree produced by jbeamParser#boolean.
    def exitBoolean(self, ctx:jbeamParser.BooleanContext):
        pass


    # Enter a parse tree produced by jbeamParser#genericString.
    def enterGenericString(self, ctx:jbeamParser.GenericStringContext):
        pass

    # Exit a parse tree produced by jbeamParser#genericString.
    def exitGenericString(self, ctx:jbeamParser.GenericStringContext):
        pass


