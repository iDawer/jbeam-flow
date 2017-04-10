import os
from collections import deque
from os import path

import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper


class ImportJBeamVehicle(Operator, ImportHelper):  #
    """Import BeamNG's JBeam vehicle"""
    bl_idname = "import_scene.jbeam_vehicle"
    bl_label = "JBeam vehicle"
    bl_options = {'REGISTER', 'UNDO'}

    directory = StringProperty(
        name="Vehicle directory",
        description="Directory used for importing the vehicle",
        maxlen=1024,
        subtype='DIR_PATH',
    )
    _timer = None

    files = []
    total = 0

    def modal(self, context, event):
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            if self.files:
                dir, name = self.files.popleft()
                context.area.header_text_set(
                    "Importing: %d/%d. Press Esc/RMB to cancel." % (self.total - len(self.files), self.total))
                bpy.ops.import_mesh.jbeam(filepath=path.join(dir, name), filename=name)
            else:
                self.report({'INFO'}, "Import done (%d parts)" % self.total)
                self.cancel(context)
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def cancel(self, context):
        context.area.header_text_set()
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def execute(self, context):
        context.screen.scene = bpy.data.scenes.new('parts')
        self.files = deque((root, f) for root, dirs, files in os.walk(self.directory)
                           for f in files if f.lower().endswith(".jbeam"))
        self.total = len(self.files)

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.2, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}


classes = (
    ImportJBeamVehicle,
)
