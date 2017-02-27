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
        self._lyr = bm_elem_seq.layers.int.new('jbeamInhProp')
        self.props_inh = props_inh  # JbeamPropsInheritance

    def next_item(self, bm_elem):
        bm_elem[self._lyr] = self._last_prop_id

    def next_prop(self, src):
        self._current_f += self.step
        prop = self.props_inh.add(self._current_f, src)
        self._last_prop_id = prop.id


class MESH_UL_jbeam_props(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        jb_prop = item

        row = layout.row(align=True)
        row.prop(jb_prop, "name", text="", emboss=False)

    def draw_filter(self, context, layout):
        # no filter
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

        layout.label('Node properties inheritance')
        row = layout.row()
        row.template_list("MESH_UL_jbeam_props", "", ob.data.jbeam_nodes_inh_props, "chain_list",
                          ob.data.jbeam_nodes_inh_props, "active_index")

        col = row.column(align=True)
        col.operator('object.jbeam_prop_inheritance_add', icon='ZOOMIN', text="")
        col.operator('object.jbeam_prop_inheritance_remove', icon='ZOOMOUT', text="")
        col.separator()
        col.operator("object.jbeam_prop_inheritance_move", icon='TRIA_UP', text="").direction = 'UP'
        col.operator("object.jbeam_prop_inheritance_move", icon='TRIA_DOWN', text="").direction = 'DOWN'

        if ob.data.jbeam_nodes_inh_props.chain_list and ob.mode == 'EDIT':
            row = layout.row()

            sub = row.row(align=True)
            sub.operator("object.jbeam_prop_inheritance_assign", text="Assign")
            sub.operator("object.jbeam_prop_inheritance_remove_from", text="Free")

            sub = row.row(align=True)
            sub.operator("object.jbeam_prop_inheritance_select", text="Select").deselect = False
            sub.operator("object.jbeam_prop_inheritance_select", text="Deselect").deselect = True

    @staticmethod
    def register():
        bpy.types.Mesh.jbeam_nodes_inh_props = PointerProperty(type=JbeamPropsInheritance)

    @staticmethod
    def unregister():
        del bpy.types.Mesh.jbeam_nodes_inh_props


class JbeamPropAdd(Operator):
    """ Add a new inherited node property to the active object """
    bl_idname = "object.jbeam_prop_inheritance_add"
    bl_label = "Add a new item"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        props = context.object.data.jbeam_nodes_inh_props
        props.new()
        props.active_index = len(props.chain_list) - 1
        return {'FINISHED'}


class JbeamPropRemove(Operator):
    """ Delete the active property from the active object and free assigned nodes """
    bl_idname = "object.jbeam_prop_inheritance_remove"
    bl_label = "Delete the active item"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props = context.object.data.jbeam_nodes_inh_props
        return props and props.active_index >= 0

    def execute(self, context):
        me = context.object.data
        props = me.jbeam_nodes_inh_props
        p_item = props.chain_list[props.active_index]

        if me.is_editmode:
            bm = bmesh.from_edit_mesh(me)
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

        inh_prop_layer = bm.verts.layers.int['jbeamInhProp']
        for v in bm.verts:
            if v[inh_prop_layer] == p_item.id:
                # inherit from root (no props)
                v[inh_prop_layer] = 0

        props.chain_list.remove(props.active_index)

        if props.active_index:
            props.active_index -= 1
        if len(props.chain_list) == 0:
            props.active_index = -1
        return {'FINISHED'}


class JbeamPropMove(Operator):
    """ Move the active property group up/down in the chain list """
    bl_idname = "object.jbeam_prop_inheritance_move"
    bl_label = "Move property group"
    bl_options = {'REGISTER', 'UNDO'}

    direction = bpy.props.EnumProperty(
        items=(
            ('UP', 'Up', ""),
            ('DOWN', 'Down', ""),
        ),
        name="Direction"
    )

    @classmethod
    def poll(cls, context):
        props = context.object.data.jbeam_nodes_inh_props
        return props and props.active_index >= 0

    def execute(self, context):
        me = context.object.data
        props = me.jbeam_nodes_inh_props
        p_item = props.chain_list[props.active_index]

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


class JbeamPropAssign(Operator):
    """ Assign the selected nodes to the active inherited property """
    bl_idname = "object.jbeam_prop_inheritance_assign"
    bl_label = "Assign"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        props = context.object.data.jbeam_nodes_inh_props
        return props and props.active_index >= 0

    def execute(self, context):
        me = context.object.data
        props = me.jbeam_nodes_inh_props
        p_item = props.chain_list[props.active_index]

        bm = bmesh.from_edit_mesh(me)
        inh_prop_layer = bm.verts.layers.int['jbeamInhProp']
        for v in bm.verts:
            if v.select:
                # override old values
                v[inh_prop_layer] = p_item.id

        return {'FINISHED'}


class JbeamPropFree(Operator):
    """ Free the selected nodes from any inherited property """
    bl_idname = "object.jbeam_prop_inheritance_remove_from"
    bl_label = "Remove from"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        me = context.object.data
        bm = bmesh.from_edit_mesh(me)
        inh_prop_layer = bm.verts.layers.int['jbeamInhProp']
        for v in bm.verts:
            if v.select:
                # inherit from root (no props)
                v[inh_prop_layer] = 0
        return {'FINISHED'}


class JbeamPropSelect(Operator):
    """ Select/deselect all nodes assigned to the active property group """
    bl_idname = "object.jbeam_prop_inheritance_select"
    bl_label = "Select"
    bl_options = {'REGISTER', 'UNDO'}

    deselect = BoolProperty(
        name="Deselect",
        description="Deselect, or not deselect, that's the question",
        default=False
    )

    @classmethod
    def poll(cls, context):
        props = context.object.data.jbeam_nodes_inh_props
        return props and props.active_index >= 0

    def execute(self, context):
        me = context.object.data
        props = me.jbeam_nodes_inh_props
        p_item = props.chain_list[props.active_index]

        bm = bmesh.from_edit_mesh(me)
        inh_prop_layer = bm.verts.layers.int['jbeamInhProp']
        for v in bm.verts:
            if v[inh_prop_layer] == p_item.id:
                v.select = not self.deselect

        # propagate selection to other selection modes (edge and face)
        bm.select_flush(not self.deselect)
        # force viewport update
        bmesh.update_edit_mesh(me, tessface=False, destructive=False)
        return {'FINISHED'}
