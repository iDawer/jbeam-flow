from bpy.types import (
    Panel,
)

from . import text_prop_editor


class JBeamPartPanel(Panel):
    bl_context = "data"
    bl_region_type = 'WINDOW'
    bl_space_type = 'PROPERTIES'
    bl_label = "JBeam Part"

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type in {'MESH'}

    def draw(self, context):
        layout = self.layout
        part = context.object.data.jbeam_part
        layout.prop(part, 'name')
        layout.prop(part, 'slot_type')
        row = layout.row(align=True)
        row.prop(part, 'data')
        op_props = row.operator(text_prop_editor.EditOperator.bl_idname, text="",
                                icon='TEXT')  # type: text_prop_editor.EditOperator
        op_props.settings.full_data_path = repr(part)
        op_props.settings.attr = 'data'


classes = (
    JBeamPartPanel,
)
