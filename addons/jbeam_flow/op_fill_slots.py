from bpy.types import Operator

from . import bl_jbeam, jbeam_utils


class FillSlots(Operator):
    """JBeam: Fill slots of selected part hierarchically."""
    bl_idname = "object.jbeam_fill_slots"
    bl_label = "JBeam: Fill slots of selected part hierarchically."

    def execute(self, context):
        part = bl_jbeam.Part(context.active_object)
        if part is None:
            self.report({'ERROR'}, "Active object is not a Part")
            return {'CANCELLED'}

        jbeam_utils.VehicleBuilder.fill_slots(part, context.scene.objects)
        return {'FINISHED'}


classes = (
    FillSlots,
)
