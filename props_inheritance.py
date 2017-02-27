from collections import OrderedDict
from time import time

import bpy
from bpy.props import IntProperty, FloatProperty, CollectionProperty, PointerProperty
from bpy.types import Panel, UIList, PropertyGroup


class PropInheritanceBuilder:
    def __init__(self, bm_elem_seq, inh_props_list):
        # property inheritance factor
        # 0 - not affected with property inheritance
        self._current_f = 0.0
        self.step = 100.0
        # A node inherits properties step by step from 0 (nothing) to last factor <= vert[_lyr]
        self._lyr = bm_elem_seq.layers.float.new('jbeamInhFactor')
        self.prop_groups = OrderedDict()
        self.inh_props_list = inh_props_list  # CollectionProperty(type=JbeamProp)

    def set_prop(self, bm_elem):
        bm_elem[self._lyr] = self._current_f

    def next_prop(self, src):
        self._current_f += self.step
        self.prop_groups[self._current_f] = src

        inh_prop = self.inh_props_list.add()
        inh_prop.name = src
        inh_prop.factor = self._current_f


class JbeamProp(bpy.types.PropertyGroup):
    # name = StringProperty() is already defined
    # id = IntProperty()
    factor = FloatProperty()


class JbeamPropsInheritance(PropertyGroup):
    list = CollectionProperty(type=JbeamProp)
    active_index = IntProperty()


class MESH_UL_jbeam_props(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        jb_prop = item

        row = layout.row(align=True)
        row.prop(jb_prop, "name", text="", emboss=False, icon_value=icon)


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
        row.template_list("MESH_UL_jbeam_props", "", ob.data.jbeam_nodes_inh_props, "list",
                          ob.data.jbeam_nodes_inh_props, "active_index")
        row = layout.row()
        row.operator('my_list.new_item')

    @staticmethod
    def register():
        bpy.types.Mesh.jbeam_nodes_inh_props = PointerProperty(type=JbeamPropsInheritance)

    @staticmethod
    def unregister():
        del bpy.types.Mesh.jbeam_nodes_inh_props


class TEST_OP(bpy.types.Operator):
    """ Add a new item to the list """

    bl_idname = "my_list.new_item"
    bl_label = "Add a new item"

    def execute(self, context):
        ob = context.object

        item = ob.data.jbeam_nodes_inh_props.list.add()
        item.name = str(time())
        return {'FINISHED'}
