import bpy
from bpy.types import Operator


class AttachToParent(Operator):
    bl_idname = "object.jbeam_attach_to_parent"
    bl_label = "JBeam: Attach to parent"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        parent = obj.parent
        # ToDo context checks



        pass

    pass