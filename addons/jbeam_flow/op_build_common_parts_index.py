import cProfile
import json
import os

import bpy
from bpy.props import StringProperty
from bpy.types import Operator

from . import jbeam_utils


class BuildCommonPartsIndexOperator(Operator):
    """JBeam: build common parts index"""
    bl_idname = "jbeam.build_common_parts_index"
    bl_label = "Build index"
    bl_options = {'REGISTER'}

    common_dir = StringProperty(
        name="Common parts directory",
        description="Common parts directory to build index from",
        maxlen=1024,
        subtype='DIR_PATH',
    )
    filepath = StringProperty(
        name="File path",
        description="Output index file",
        maxlen=1024,
        subtype='FILE_PATH',
    )

    def execute(self, context):
        # profiler = cProfile.Profile()
        # profiler.enable()

        idx_builder = jbeam_utils.PartsIndexBuilder()
        idx_builder.directory(bpy.path.abspath(self.common_dir))
        idx_path = bpy.path.abspath(self.filepath)
        mode = 'w' if os.path.isfile(idx_path) else 'x'
        with open(idx_path, mode, encoding='utf-8') as file:
            json.dump(idx_builder.index, file)

        # profiler.disable()
        # profiler.dump_stats(r'C:\Users\Dawer\AppData\Roaming\Blender '
        #                     r'Foundation\Blender\2.78\scripts\addons\BlenderJBeam\profile\ImportJBeam.pstat')
        # profiler.clear()

        return {'FINISHED'}


classes = (
    BuildCommonPartsIndexOperator,
)
