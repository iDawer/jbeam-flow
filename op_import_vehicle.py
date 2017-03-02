import os
from os import path
from itertools import chain

import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
# from bpy import path
from bpy_extras.io_utils import ImportHelper

from . import jbeam_utils


class ImportJBeam(Operator, ImportHelper):
    """Import from BeamNG's JBeam vehicle"""
    bl_idname = "import_scene.jbeam_vehicle"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "JBeam vehicle"
    bl_options = {'REGISTER', 'UNDO'}

    directory = StringProperty(
        name="File Path",
        description="Filepath used for importing the file",
        maxlen=1024,
        subtype='DIR_PATH',
    )

    def execute(self, context):
        files = ((root, f) for root, dirs, files in os.walk(self.directory)
                 for f in files if f.lower().endswith(".jbeam"))

        for dir, name in files:
            bpy.ops.import_mesh.jbeam(filepath=path.join(dir, name), filename=name)

        # builder = jbeam_utils.PartObjectsBuilder(text_block.name)
        # parts_group = builder.visit(tree)
        #
        # # resulting parts_group and text names can be different
        # parts_group['jbeam_textblock'] = text_block.name
        # for obj in builder.get_all_objects():
        #     context.scene.objects.link(obj)

        return {'FINISHED'}

        # @staticmethod
        # def register():
        #     bpy.types.INFO_MT_file_import.append(menu_func_draw)
        #
        # @staticmethod
        # def unregister():
        #     bpy.types.INFO_MT_file_import.remove(menu_func_draw)
        #


def menu_func_draw(self, context):
    self.layout.operator(ImportJBeam.bl_idname)
