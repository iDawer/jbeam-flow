from collections import OrderedDict
from time import time

import bpy
from bpy.props import IntProperty, FloatProperty, CollectionProperty, PointerProperty
from bpy.types import Panel, UIList, PropertyGroup


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


class JbeamProp(bpy.types.PropertyGroup):
    # name = StringProperty() is already defined
    id = IntProperty()
    factor = FloatProperty()


class JbeamPropsInheritance(PropertyGroup):
    """
    Represents properties inheritance chaining.
    Position in the chain described with factor (float number).
    Item with factor N inherits all props in the chain with factor less or equal to N with priority of the last.
    """
    chain_list = CollectionProperty(type=JbeamProp)
    active_index = IntProperty()
    last_id = IntProperty()

    def add(self, factor, src):
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

        item = ob.data.jbeam_nodes_inh_props.new()
        # item.name = str(time())
        return {'FINISHED'}
