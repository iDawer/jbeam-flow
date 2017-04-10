from itertools import cycle, islice

import bmesh
import bpy
from bpy.props import (
    BoolProperty,
)
from bpy.types import (
    Panel,
    UIList,
    Operator,
)

from . import bl_jbeam


class PropsMixin:
    def draw_item(self, context, layout: bpy.types.UILayout, data: bl_jbeam.PropsTable, item: bl_jbeam.PropsTable.Prop,
                  icon, active_data, active_propname):
        jb_prop = item

        row = layout.row(align=True)
        row.prop(jb_prop, "src", text="", emboss=False)
        # counter
        str_id = str(item.id)
        if str_id in data.counter:
            split = row.split()
            split.alignment = 'RIGHT'
            split.label(text=str(data.counter[str_id]), icon='PINNED')

    def draw_filter(self, context, layout):
        # no filter
        pass


# list shares events between his instances, so we need to create different classes per section
class MESH_UL_jbeam_nodes(PropsMixin, UIList):
    pass


class MESH_UL_jbeam_beams(PropsMixin, UIList):
    pass


class MESH_UL_jbeam_triangles(PropsMixin, UIList):
    pass


class MESH_UL_jbeam_quads(PropsMixin, UIList):
    pass


class JbeamPanel:
    bl_context = "data"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type in {'MESH'}

    @staticmethod
    def template_props_table(layout: bpy.types.UILayout, props_table: bl_jbeam.PropsTable, listtype_name: str,
                             add_operator: str, remove_operator: str, move_operator: str,
                             object_mode: str, assign_operator: str, free_operator: str, select_operator: str):
        row = layout.row()
        row.template_list(listtype_name, "", props_table, "chain_list",
                          props_table, "active_index")

        col = row.column(align=True)
        col.operator(add_operator, icon='ZOOMIN', text="")
        col.operator(remove_operator, icon='ZOOMOUT', text="")
        col.separator()
        col.operator(move_operator, icon='TRIA_UP', text="").direction = 'UP'
        col.operator(move_operator, icon='TRIA_DOWN', text="").direction = 'DOWN'

        if props_table.chain_list and object_mode == 'EDIT':
            row = layout.row()

            sub = row.row(align=True)
            sub.operator(assign_operator, text="Assign")
            sub.operator(free_operator, text="Free")

            sub = row.row(align=True)
            sub.operator(select_operator, text="Select").select = True
            sub.operator(select_operator, text="Deselect").select = False


class DATA_PT_jbeam_nodes(JbeamPanel, Panel):
    bl_label = "JBeam Nodes"

    def draw(self, context):
        layout = self.layout
        ob = context.object

        self.template_props_table(layout, ob.data.jbeam_node_prop_chain, MESH_UL_jbeam_nodes.__name__,
                                  NodePropChain_Add.bl_idname,
                                  NodePropChain_Remove.bl_idname,
                                  NodePropChain_Move.bl_idname,
                                  ob.mode,
                                  NodePropChain_Assign.bl_idname,
                                  NodePropChain_Free.bl_idname,
                                  NodePropChain_Select.bl_idname)


class DATA_PT_jbeam_beams(JbeamPanel, Panel):
    bl_label = "JBeam Beams"

    def draw(self, context):
        layout = self.layout
        ob = context.object

        self.template_props_table(layout, ob.data.jbeam_beam_prop_chain, MESH_UL_jbeam_beams.__name__,
                                  BeamPropChain_Add.bl_idname,
                                  BeamPropChain_Remove.bl_idname,
                                  BeamPropChain_Move.bl_idname,
                                  ob.mode,
                                  BeamPropChain_Assign.bl_idname,
                                  BeamPropChain_Free.bl_idname,
                                  BeamPropChain_Select.bl_idname)


class DATA_PT_jbeam_triangles(JbeamPanel, Panel):
    bl_label = "JBeam Triangles"

    def draw(self, context):
        layout = self.layout
        ob = context.object

        self.template_props_table(layout, ob.data.jbeam_triangle_prop_chain, MESH_UL_jbeam_triangles.__name__,
                                  TrianglePropChain_Add.bl_idname,
                                  TrianglePropChain_Remove.bl_idname,
                                  TrianglePropChain_Move.bl_idname,
                                  ob.mode,
                                  TrianglePropChain_Assign.bl_idname,
                                  TrianglePropChain_Free.bl_idname,
                                  TrianglePropChain_Select.bl_idname)


class DATA_PT_jbeam_quads(JbeamPanel, Panel):
    bl_label = "JBeam Quads"

    def draw(self, context):
        layout = self.layout
        ob = context.object

        self.template_props_table(layout, ob.data.jbeam_quads_ptable, MESH_UL_jbeam_quads.__name__,
                                  QuadPropChain_Add.bl_idname,
                                  QuadPropChain_Remove.bl_idname,
                                  QuadPropChain_Move.bl_idname,
                                  ob.mode,
                                  QuadPropChain_Assign.bl_idname,
                                  QuadPropChain_Free.bl_idname,
                                  QuadPropChain_Select.bl_idname)


class PropSetBase:
    bl_options = {'REGISTER', 'UNDO'}

    @staticmethod
    def get_props(context) -> bl_jbeam.PropsTable:
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
        props.new_prop()
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
        ids = []
        for elem in self.get_bm_elements(bm):
            if elem.select:
                # override old values
                elem[inh_prop_layer] = p_item.id
            ids.append(str(elem[inh_prop_layer]))

        props.update_counter(ids)
        return {'FINISHED'}


class PropSet_Free(PropSetBase):
    def execute(self, context):
        me = context.object.data
        bm = bmesh.from_edit_mesh(me)
        inh_prop_layer = self.get_datalayer(bm)
        ids = []
        for elem in self.get_bm_elements(bm):
            if elem.select:
                # inherit from root (no props)
                elem[inh_prop_layer] = 0
            ids.append(str(elem[inh_prop_layer]))

        self.get_props(context).update_counter(ids)
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
        ids = []
        for elem in self.get_bm_elements(bm):
            if elem[inh_prop_layer] == p_item.id:
                elem.select = self.select
            ids.append(str(elem[inh_prop_layer]))

        props.update_counter(ids)
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
        dlayer = bm.verts.layers.int.get(bl_jbeam.PROP_CHAIN_ID, None)
        if dlayer is None:
            dlayer = bm.verts.layers.int.new(bl_jbeam.PROP_CHAIN_ID)
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
        dlayer = bm.edges.layers.int.get(bl_jbeam.PROP_CHAIN_ID, None)
        if dlayer is None:
            dlayer = bm.edges.layers.int.new(bl_jbeam.PROP_CHAIN_ID)
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
        dlayer = bm.faces.layers.int.get(bl_jbeam.PROP_CHAIN_ID, None)
        if dlayer is None:
            dlayer = bm.faces.layers.int.new(bl_jbeam.PROP_CHAIN_ID)
        return dlayer

    @staticmethod
    def get_bm_elements(bm):
        return bm.faces


class QuadsOpMixin(PropSetBase):
    @staticmethod
    def get_props(context):
        return context.object.data.jbeam_quads_ptable

    @staticmethod
    def get_datalayer(bm: bmesh.types.BMesh):
        return bl_jbeam.QuadsPropTable.get_id_layer(bm.faces)

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


# ====================== quads =====================================================================================

class QuadPropChain_Add(QuadsOpMixin, PropSet_Add, Operator):
    """Add a new property set to the quads section of the active object """
    bl_idname = "object.jbeam_quad_prop_chain_add"
    bl_label = "Add a new property set to the quads section"


class QuadPropChain_Remove(QuadsOpMixin, PropSet_Remove, Operator):
    """Delete the active property from the active object and free assigned quads """
    bl_idname = "object.jbeam_quad_prop_chain_remove"
    bl_label = "Delete the active item"


class QuadPropChain_Move(QuadsOpMixin, PropSet_Move, Operator):
    """Move the active property group up/down in the chain list """
    bl_idname = "object.jbeam_quad_prop_chain_move"
    bl_label = "Move property group"


class QuadPropChain_Assign(QuadsOpMixin, PropSet_Assign, Operator):
    """Assign the selected quads to the active property set.
Note, a quad can be assigned to only one element of the chain.
"""
    bl_idname = "object.jbeam_quad_prop_chain_assign"
    bl_label = "Assign"


class QuadPropChain_Free(QuadsOpMixin, PropSet_Free, Operator):
    """Free the selected quads from any inherited property """
    bl_idname = "object.jbeam_quad_prop_chain_free"
    bl_label = "Remove from"


class QuadPropChain_Select(QuadsOpMixin, PropSet_Select, Operator):
    """Select/deselect all quads assigned to the active property set """
    bl_idname = "object.jbeam_quad_prop_chain_select"
    bl_label = "Select"


classes = (
    MESH_UL_jbeam_nodes,
    MESH_UL_jbeam_beams,
    MESH_UL_jbeam_triangles,
    MESH_UL_jbeam_quads,

    DATA_PT_jbeam_nodes,
    DATA_PT_jbeam_beams,
    DATA_PT_jbeam_triangles,
    DATA_PT_jbeam_quads,

    NodePropChain_Add,
    NodePropChain_Remove,
    NodePropChain_Move,
    NodePropChain_Assign,
    NodePropChain_Free,
    NodePropChain_Select,

    BeamPropChain_Add,
    BeamPropChain_Remove,
    BeamPropChain_Move,
    BeamPropChain_Assign,
    BeamPropChain_Free,
    BeamPropChain_Select,

    TrianglePropChain_Add,
    TrianglePropChain_Remove,
    TrianglePropChain_Move,
    TrianglePropChain_Assign,
    TrianglePropChain_Free,
    TrianglePropChain_Select,

    QuadPropChain_Add,
    QuadPropChain_Remove,
    QuadPropChain_Move,
    QuadPropChain_Assign,
    QuadPropChain_Free,
    QuadPropChain_Select,
)
