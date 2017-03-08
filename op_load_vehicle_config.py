import json
from collections import defaultdict
from itertools import takewhile

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from antlr4 import *
from .misc import Switch, anytree, visitor_mixins as vmix
from .jb import jbeamVisitor, jbeamParser, jbeamLexer
from . import jbeam_utils


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
                slotType = ob.data.get('slotType')
                part_name = ob.data.get('jbeam_part')
                if slotType is not None and part_name is not None:
                    part_map[slotType][part_name] = ob
            elif is_slot(ob):
                part_name = ob.parent.parent.data.get('jbeam_part')
                part_slots_map[part_name].append((ob.name.partition('.')[0], ob['default'], ob))

        main_parts = part_map.get('main')
        if main_parts is None or len(main_parts) == 0:
            self.report({'ERROR'}, "main slot not found")
            return {'CANCELLED'}
        main_p = next(iter(main_parts.values()))

        with open(self.filepath, encoding='utf-8') as pc_file:
            pc = decode_json(pc_file.read())
        fill_slots(part_map, part_slots_map, main_p, pc['parts'], 0)

        # clean up unused parts
        for ob in context.scene.objects:
            if ob.parent is None and ob != main_p:  # checking with 'is' will fail (internal BL object wrapping)
                bpy.data.objects.remove(ob, do_unlink=True)
        return {'FINISHED'}


def fill_slots(part_map: defaultdict(dict), part_slots_map: defaultdict(list), part, slot_part_conf: dict,
               depth: int):
    if depth > 50:
        print("WARNING: Slots tree too deep (>50). Current part: '{}'".format(part.name))
        return

    part_name = part.data['jbeam_part']
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
                print("Part '{}' for slot [{}] not found".format(ch_part_name, slot_name))


def is_slot(ob):
    return ob.parent is not None and 'slots' == ob.parent.name.partition('.')[0]


# class Node(anytree.Node):
#     """Tree node, simple repr()"""
#
#     def __repr__(self):
#         return self.name
#
# class SlotNode(Node):
#     pass

def decode_json(data: str):
    data_stream = InputStream(data)

    lexer = jbeamLexer(data_stream)
    stream = CommonTokenStream(lexer)
    parser = jbeamParser(stream)
    obj_ctx = parser.obj()
    result = obj_ctx.accept(vmix.Json())
    return result


class VConf(jbeamVisitor):
    def __init__(self, part_map):
        self.part_map = part_map

    # def visit_pc(self, ctx: jbeamParser.ObjContext):
    #     for keyValCtx in ctx.keyVal():
    #         with Switch(keyValCtx.key.string_item) as case:
    #             if case('parts'):
    #                 self.visit_parts(keyValCtx.val)
    #
    # def visit_parts(self, ctx: jbeamParser.ObjectValueContext):
    #     for slot_part in ctx.obj().keyVal():
    #         pass

    pass
