from collections import OrderedDict
from itertools import cycle, islice
from time import time

import bmesh
import bpy
from bpy.props import (
    IntProperty,
    FloatProperty,
    CollectionProperty,
    PointerProperty,
    BoolProperty,
    EnumProperty,
)
from bpy.types import (
    Panel,
    UIList,
    PropertyGroup,
    Operator,
)

PROP_CHAIN_ID = 'jbeam_prop_chain_id'


class JbeamProp(PropertyGroup):
    # name = StringProperty() is already defined
    # 'id' is a reference for nodes
    id = IntProperty()
    factor = FloatProperty()


class JbeamPropsInheritance(PropertyGroup):
    """
    Represents properties inheritance chaining.
    Position in the chain described with factor (float number).
    Item with factor N inherits all props in the chain with factor less or equal to N with priority of the last.
    """
    chain_list = CollectionProperty(type=JbeamProp)
    active_index = IntProperty(default=-1)
    last_id = IntProperty()

    def add(self, factor, src):
        # ids start from 1, default 0 is root of the chain
        self.last_id += 1
        prop_item = self.chain_list.add()
        prop_item.id = self.last_id
        prop_item.name = src
        prop_item.factor = factor
        return prop_item

    def new(self):
        factor = 0  # root
        if len(self.chain_list):
            last_inh_prop = sorted(self.chain_list, key=lambda p: p.factor)[-1]
            factor = last_inh_prop.factor
        return self.add(factor + 100, "{}")


class PropInheritanceBuilder:
    def __init__(self, bm_elem_seq, props_inh: JbeamPropsInheritance):
        self._last_prop_id = 0
        # property inheritance factor
        # 0 - not affected with property inheritance
        self._current_f = 0.0
        self.step = 100.0
        # A node inherits properties step by step from 0 (nothing) to last factor <= vert[_lyr]
        self._lyr = bm_elem_seq.layers.int.new(PROP_CHAIN_ID)
        self.props_inh = props_inh  # JbeamPropsInheritance

    def next_item(self, bm_elem):
        bm_elem[self._lyr] = self._last_prop_id

    def next_prop(self, src):
        self._current_f += self.step
        prop = self.props_inh.add(self._current_f, src)
        self._last_prop_id = prop.id


class ChainListMixin:
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        jb_prop = item

        row = layout.row(align=True)
        row.prop(jb_prop, "name", text="", emboss=False)

    def draw_filter(self, context, layout):
        # no filter
        pass


# list shares events between his instances, so we need to create different classes per section
class MESH_UL_jbeam_node_chain(ChainListMixin, UIList):
    pass


class MESH_UL_jbeam_beam_chain(ChainListMixin, UIList):
    pass


class MESH_UL_jbeam_triangle_chain(ChainListMixin, UIList):
    pass


class DATA_PT_jbeam(Panel):
    bl_label = "JBeam"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type in {'MESH'}

    def draw(self, context):
        layout = self.layout
        ob = context.object

        # ============= nodes
        layout.label('Node chain of property inheritance')
        row = layout.row()
        row.template_list("MESH_UL_jbeam_node_chain", "", ob.data.jbeam_node_prop_chain, "chain_list",
                          ob.data.jbeam_node_prop_chain, "active_index")

        col = row.column(align=True)
        col.operator(NodePropChain_Add.bl_idname, icon='ZOOMIN', text="")
        col.operator(NodePropChain_Remove.bl_idname, icon='ZOOMOUT', text="")
        col.separator()
        col.operator(NodePropChain_Move.bl_idname, icon='TRIA_UP', text="").direction = 'UP'
        col.operator(NodePropChain_Move.bl_idname, icon='TRIA_DOWN', text="").direction = 'DOWN'

        if ob.data.jbeam_node_prop_chain.chain_list and ob.mode == 'EDIT':
            row = layout.row()

            sub = row.row(align=True)
            sub.operator(NodePropChain_Assign.bl_idname, text="Assign")
            sub.operator(NodePropChain_Free.bl_idname, text="Free")

            sub = row.row(align=True)
            sub.operator(NodePropChain_Select.bl_idname, text="Select").select = True
            sub.operator(NodePropChain_Select.bl_idname, text="Deselect").select = False

        # ============= beams
        layout.label('Beam chain of property inheritance')
        row = layout.row()
        row.template_list("MESH_UL_jbeam_beam_chain", "", ob.data.jbeam_beam_prop_chain, "chain_list",
                          ob.data.jbeam_beam_prop_chain, "active_index")

        col = row.column(align=True)
        col.operator(BeamPropChain_Add.bl_idname, icon='ZOOMIN', text="")
        col.operator(BeamPropChain_Remove.bl_idname, icon='ZOOMOUT', text="")
        col.separator()
        col.operator(BeamPropChain_Move.bl_idname, icon='TRIA_UP', text="").direction = 'UP'
        col.operator(BeamPropChain_Move.bl_idname, icon='TRIA_DOWN', text="").direction = 'DOWN'

        if ob.data.jbeam_beam_prop_chain.chain_list and ob.mode == 'EDIT':
            row = layout.row()

            sub = row.row(align=True)
            sub.operator(BeamPropChain_Assign.bl_idname, text="Assign")
            sub.operator(BeamPropChain_Free.bl_idname, text="Free")

            sub = row.row(align=True)
            sub.operator(BeamPropChain_Select.bl_idname, text="Select").select = True
            sub.operator(BeamPropChain_Select.bl_idname, text="Deselect").select = False

        # ============= triangles
        layout.label('Triangle chain of property inheritance')
        row = layout.row()
        row.template_list("MESH_UL_jbeam_triangle_chain", "", ob.data.jbeam_triangle_prop_chain, "chain_list",
                          ob.data.jbeam_triangle_prop_chain, "active_index")

        col = row.column(align=True)
        col.operator(TrianglePropChain_Add.bl_idname, icon='ZOOMIN', text="")
        col.operator(TrianglePropChain_Remove.bl_idname, icon='ZOOMOUT', text="")
        col.separator()
        col.operator(TrianglePropChain_Move.bl_idname, icon='TRIA_UP', text="").direction = 'UP'
        col.operator(TrianglePropChain_Move.bl_idname, icon='TRIA_DOWN', text="").direction = 'DOWN'

        if ob.data.jbeam_triangle_prop_chain.chain_list and ob.mode == 'EDIT':
            row = layout.row()

            sub = row.row(align=True)
            sub.operator(TrianglePropChain_Assign.bl_idname, text="Assign")
            sub.operator(TrianglePropChain_Free.bl_idname, text="Free")

            sub = row.row(align=True)
            sub.operator(TrianglePropChain_Select.bl_idname, text="Select").select = True
            sub.operator(TrianglePropChain_Select.bl_idname, text="Deselect").select = False

    @staticmethod
    def register():
        bpy.types.Mesh.jbeam_node_prop_chain = PointerProperty(type=JbeamPropsInheritance)
        bpy.types.Mesh.jbeam_beam_prop_chain = PointerProperty(type=JbeamPropsInheritance)
        bpy.types.Mesh.jbeam_triangle_prop_chain = PointerProperty(type=JbeamPropsInheritance)

    @staticmethod
    def unregister():
        del bpy.types.Mesh.jbeam_node_prop_chain
        del bpy.types.Mesh.jbeam_beam_prop_chain
        del bpy.types.Mesh.jbeam_triangle_prop_chain


class PropSetBase:
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def get_props(context):
        raise NotImplementedError('Abstract method call')

    @staticmethod
    def get_datalayer(bm):
        raise NotImplementedError('Abstract method call')

    @staticmethod
    def get_bm_elements(bm):
        raise NotImplementedError('Abstract method call')


class PropSet_Add(PropSetBase):
    def execute(self, context):
        props = self.get_props(context)
        props.new()
        next_idx = props.active_index + 1
        # smart add after current selected item
        props.chain_list.move(len(props.chain_list) - 1, next_idx)
        props.active_index = next_idx
        return {'FINISHED'}


class PropSet_Remove(PropSetBase):
    @classmethod
    def poll(cls, context):
        props = cls.get_props(context)
        return props and props.active_index >= 0

    def execute(self, context):
        me = context.object.data
        props = self.get_props(context)
        p_item = props.chain_list[props.active_index]

        if me.is_editmode:
            bm = bmesh.from_edit_mesh(me)
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

        inh_prop_layer = self.get_datalayer(bm)
        for elem in self.get_bm_elements(bm):
            if elem[inh_prop_layer] == p_item.id:
                # inherit from root (no props)
                elem[inh_prop_layer] = 0

        props.chain_list.remove(props.active_index)

        if props.active_index:
            props.active_index -= 1
        if len(props.chain_list) == 0:
            props.active_index = -1
        return {'FINISHED'}


class PropSet_Move(PropSetBase):
    direction = bpy.props.EnumProperty(
        items=(
            ('UP', 'Up', ""),
            ('DOWN', 'Down', ""),
        ),
        name="Direction"
    )

    @classmethod
    def poll(cls, context):
        props = cls.get_props(context)
        return props and props.active_index >= 0

    def execute(self, context):
        props = self.get_props(context)
        # p_item = props.chain_list[props.active_index]

        idx = props.active_index
        _len = len(props.chain_list)
        if self.direction == 'DOWN':
            # get next index in cycled range
            new_idx = next(islice(cycle(range(0, _len)), idx + 1, None))
        elif self.direction == 'UP':
            # get prev index in cycled range
            new_idx = next(islice(cycle(reversed(range(0, _len))), _len - idx, None))
        else:
            return {'CANCELLED'}
        props.chain_list.move(idx, new_idx)
        props.active_index = new_idx
        return {'FINISHED'}


class PropSet_Assign(PropSetBase):
    @classmethod
    def poll(cls, context):
        props = cls.get_props(context)
        return props and props.active_index >= 0

    def execute(self, context):
        me = context.object.data
        props = self.get_props(context)
        p_item = props.chain_list[props.active_index]

        bm = bmesh.from_edit_mesh(me)
        inh_prop_layer = self.get_datalayer(bm)
        for elem in self.get_bm_elements(bm):
            if elem.select:
                # override old values
                elem[inh_prop_layer] = p_item.id

        return {'FINISHED'}


class PropSet_Free(PropSetBase):
    def execute(self, context):
        me = context.object.data
        bm = bmesh.from_edit_mesh(me)
        inh_prop_layer = self.get_datalayer(bm)
        for elem in self.get_bm_elements(bm):
            if elem.select:
                # inherit from root (no props)
                elem[inh_prop_layer] = 0
        return {'FINISHED'}


class PropSet_Select(PropSetBase):
    select = BoolProperty(
        name="Select",
        description="Select, or deselect, that's the question",
        default=True
    )

    @classmethod
    def poll(cls, context):
        props = cls.get_props(context)
        return props and props.active_index >= 0

    def execute(self, context):
        me = context.object.data
        props = self.get_props(context)
        p_item = props.chain_list[props.active_index]

        bm = bmesh.from_edit_mesh(me)
        inh_prop_layer = self.get_datalayer(bm)
        for elem in self.get_bm_elements(bm):
            if elem[inh_prop_layer] == p_item.id:
                elem.select = self.select

        # propagate selection to other selection modes (edge and face)
        # bm.select_flush(self.select)
        # force viewport update
        bmesh.update_edit_mesh(me, tessface=False, destructive=False)
        return {'FINISHED'}


class NodesOpMixin(PropSetBase):
    @staticmethod
    def get_props(context):
        return context.object.data.jbeam_node_prop_chain

    @staticmethod
    def get_datalayer(bm):
        dlayer = bm.verts.layers.int.get(PROP_CHAIN_ID, None)
        if dlayer is None:
            dlayer = bm.verts.layers.int.new(PROP_CHAIN_ID)
        return dlayer

    @staticmethod
    def get_bm_elements(bm):
        return bm.verts


class BeamsOpMixin(PropSetBase):
    @staticmethod
    def get_props(context):
        return context.object.data.jbeam_beam_prop_chain

    @staticmethod
    def get_datalayer(bm):
        dlayer = bm.edges.layers.int.get(PROP_CHAIN_ID, None)
        if dlayer is None:
            dlayer = bm.edges.layers.int.new(PROP_CHAIN_ID)
        return dlayer

    @staticmethod
    def get_bm_elements(bm):
        return bm.edges


class TrianglesOpMixin(PropSetBase):
    @staticmethod
    def get_props(context):
        return context.object.data.jbeam_triangle_prop_chain

    @staticmethod
    def get_datalayer(bm):
        dlayer = bm.faces.layers.int.get(PROP_CHAIN_ID, None)
        if dlayer is None:
            dlayer = bm.faces.layers.int.new(PROP_CHAIN_ID)
        return dlayer

    @staticmethod
    def get_bm_elements(bm):
        return bm.faces


# ====================== nodes =========================================================================================
class NodePropChain_Add(NodesOpMixin, PropSet_Add, Operator):
    """Add a new property set to the nodes section of the active object """
    bl_idname = "object.jbeam_node_prop_chain_add"
    bl_label = "Add a new property set to the nodes section"


class NodePropChain_Remove(NodesOpMixin, PropSet_Remove, Operator):
    """Delete the active property from the active object and free assigned nodes """
    bl_idname = "object.jbeam_node_prop_chain_remove"
    bl_label = "Delete the active item"


class NodePropChain_Move(NodesOpMixin, PropSet_Move, Operator):
    """Move the active property group up/down in the chain list """
    bl_idname = "object.jbeam_node_prop_chain_move"
    bl_label = "Move property group"


class NodePropChain_Assign(NodesOpMixin, PropSet_Assign, Operator):
    """Assign the selected nodes to the active property set.
Note, a node can be assigned to only one element of the chain.
"""
    bl_idname = "object.jbeam_node_prop_chain_assign"
    bl_label = "Assign"


class NodePropChain_Free(NodesOpMixin, PropSet_Free, Operator):
    """Free the selected nodes from any inherited property """
    bl_idname = "object.jbeam_node_prop_chain_free"
    bl_label = "Remove from"


class NodePropChain_Select(NodesOpMixin, PropSet_Select, Operator):
    """Select/deselect all nodes assigned to the active property set """
    bl_idname = "object.jbeam_node_prop_chain_select"
    bl_label = "Select"


# ====================== beams =========================================================================================
class BeamPropChain_Add(BeamsOpMixin, PropSet_Add, Operator):
    """Add a new property set to the beams section of the active object """
    bl_idname = "object.jbeam_beam_prop_chain_add"
    bl_label = "Add a new property set to the beams section"


class BeamPropChain_Remove(BeamsOpMixin, PropSet_Remove, Operator):
    """Delete the active property from the active object and free assigned beams """
    bl_idname = "object.jbeam_beam_prop_chain_remove"
    bl_label = "Delete the active item"


class BeamPropChain_Move(BeamsOpMixin, PropSet_Move, Operator):
    """Move the active property group up/down in the chain list """
    bl_idname = "object.jbeam_beam_prop_chain_move"
    bl_label = "Move property group"


class BeamPropChain_Assign(BeamsOpMixin, PropSet_Assign, Operator):
    """Assign the selected beams to the active property set.
Note, a beam can be assigned to only one element of the chain.
"""
    bl_idname = "object.jbeam_beam_prop_chain_assign"
    bl_label = "Assign"


class BeamPropChain_Free(BeamsOpMixin, PropSet_Free, Operator):
    """Free the selected beams from any inherited property """
    bl_idname = "object.jbeam_beam_prop_chain_free"
    bl_label = "Remove from"


class BeamPropChain_Select(BeamsOpMixin, PropSet_Select, Operator):
    """Select/deselect all beams assigned to the active property set """
    bl_idname = "object.jbeam_beam_prop_chain_select"
    bl_label = "Select"


# ====================== triangles =====================================================================================
class TrianglePropChain_Add(TrianglesOpMixin, PropSet_Add, Operator):
    """Add a new property set to the triangles section of the active object """
    bl_idname = "object.jbeam_triangle_prop_chain_add"
    bl_label = "Add a new property set to the triangles section"


class TrianglePropChain_Remove(TrianglesOpMixin, PropSet_Remove, Operator):
    """Delete the active property from the active object and free assigned triangles """
    bl_idname = "object.jbeam_triangle_prop_chain_remove"
    bl_label = "Delete the active item"


class TrianglePropChain_Move(TrianglesOpMixin, PropSet_Move, Operator):
    """Move the active property group up/down in the chain list """
    bl_idname = "object.jbeam_triangle_prop_chain_move"
    bl_label = "Move property group"


class TrianglePropChain_Assign(TrianglesOpMixin, PropSet_Assign, Operator):
    """Assign the selected triangles to the active property set.
Note, a triangle can be assigned to only one element of the chain.
"""
    bl_idname = "object.jbeam_triangle_prop_chain_assign"
    bl_label = "Assign"


class TrianglePropChain_Free(TrianglesOpMixin, PropSet_Free, Operator):
    """Free the selected triangles from any inherited property """
    bl_idname = "object.jbeam_triangle_prop_chain_free"
    bl_label = "Remove from"


class TrianglePropChain_Select(TrianglesOpMixin, PropSet_Select, Operator):
    """Select/deselect all triangles assigned to the active property set """
    bl_idname = "object.jbeam_triangle_prop_chain_select"
    bl_label = "Select"