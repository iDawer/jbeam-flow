from collections import defaultdict

import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from .jbeam import ext_json


class LoadVehicleConfig(Operator, ImportHelper):
    bl_idname = "import_scene.jbeam_vehicle_config"
    bl_label = "JBeam: Load vehicle config (.pc)"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".pc"

    filter_glob = StringProperty(
        default="*.pc",
        options={'HIDDEN'},
    )

    filename = StringProperty(
        name="File Name",
        description="Filename used for importing the file",
        maxlen=255,
        subtype='FILE_NAME',
        options={'HIDDEN'},
    )

    def execute(self, context):
        scene_parts = bpy.data.scenes.get('parts')
        if scene_parts is None:
            self.report({'ERROR'}, "'parts' scene not found")
            return {'CANCELLED'}

        context.screen.scene = scene_parts
        # make object data linked copy of 'parts' scene
        bpy.ops.scene.new(type='LINK_OBJECT_DATA')
        context.scene.name = self.filename
        # clear duplicate groups
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.group.objects_remove_all()

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
                part_slots_map[part_name].append((ob.name.partition('.')[0], ob.jbeam_slot.default, ob))

        main_parts = part_map.get('main')
        if not main_parts:
            self.report({'ERROR'}, "Part with slot type 'main' not found")
            return {'CANCELLED'}
        main_p = next(iter(main_parts.values()))

        print("Loading vehicle config '{}'".format(self.filename))
        with open(self.filepath, encoding='utf-8') as pc_file:
            pc = PC.load_from(pc_file)
        fill_slots(part_map, part_slots_map, main_p, pc.parts, 0)

        # clean up unused parts
        for ob in context.scene.objects:
            if ob.parent is None and ob != main_p:  # checking with 'is not' will fail (internal BL object wrapping)
                bpy.data.objects.remove(ob, do_unlink=True)
        return {'FINISHED'}


class PC:
    @staticmethod
    def load_from(file):
        data = ext_json.load(file.read())
        ft = data.get('format')
        if ft:
            p = PC.Format2(data)
            p.format = ft
            return p
        return PC.Default(data)

    class Default:
        format = 1

        def __init__(self, pc_data: dict):
            self.data = pc_data

        @property
        def parts(self):
            return self.data

    class Format2(Default):
        format = 2

        @property
        def parts(self):
            return self.data['parts']


def fill_slots(part_map: defaultdict(dict), part_slots_map: defaultdict(list), part, slot_part_conf: dict,
               depth: int):
    if depth > 50:
        print("\tWARNING: Slots tree too deep (>50). Current part: '{}'".format(part.name))
        return

    part_name = part.data.jbeam_part.name
    for slot_name, default, slot_obj in part_slots_map[part_name]:
        ch_part_name = slot_part_conf.get(slot_name) or default
        if ch_part_name:
            # child part specified by 'pc' or default
            ch_part = part_map[slot_name].get(ch_part_name)
            if ch_part is not None:  # child part found
                ch_part.parent = slot_obj
                fill_slots(part_map, part_slots_map, ch_part, slot_part_conf, depth + 1)
            else:
                # child part specified but not found
                print("\tPart '{}' for slot [{}] not found".format(ch_part_name, slot_name))


classes = (
    LoadVehicleConfig,
)
