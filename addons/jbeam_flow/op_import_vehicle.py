import os
from collections import deque, defaultdict
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
                # All files imported. Filling slots:
                part_map = defaultdict(dict)
                part_slots_map = defaultdict(list)
                for ob in context.scene.objects:
                    if ob.type == 'MESH':
                        slotType = ob.data.jbeam_part.slot_type
                        part_name = ob.data.jbeam_part.name
                        if slotType is not None and part_name is not None:
                            part_map[slotType][part_name] = ob
                    elif ob.jbeam_slot.is_slot():
                        part_name = ob.parent.parent.data.jbeam_part.name
                        part_slots_map[part_name].append(ob.jbeam_slot)

                main_parts = part_map.get('main')
                if not main_parts:
                    self.report({'ERROR'}, "Missing part with slot type 'main'")
                    self.cancel(context)
                    return {'CANCELLED'}
                main_p = next(iter(main_parts.values()))
                fill_slots(part_map, part_slots_map, main_p)

                self.report({'INFO'}, "Import done (%d files)" % self.total)
                self.cancel(context)
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def cancel(self, context):
        context.area.header_text_set()
        wm = context.window_manager
        wm.event_timer_remove(self._timer)

    def execute(self, context):
        vehicle_name = path.basename(path.dirname(self.directory))
        context.screen.scene = bpy.data.scenes.new(vehicle_name)
        self.files = deque((root, f) for root, dirs, files in os.walk(self.directory)
                           for f in files if f.lower().endswith(".jbeam"))
        self.total = len(self.files)

        wm = context.window_manager
        self._timer = wm.event_timer_add(0.2, context.window)
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}


def fill_slots(part_map: defaultdict(dict), part_slots_map: defaultdict(list), part):
    part_name = part.data.jbeam_part.name
    for slot in part_slots_map[part_name]:
        for ch_part in part_map[slot.type].values():
            # ToDo handle already parented objects (duplicate?)
            slot.add_part_object(ch_part)
            fill_slots(part_map, part_slots_map, ch_part)


classes = (
    ImportJBeamVehicle,
)
