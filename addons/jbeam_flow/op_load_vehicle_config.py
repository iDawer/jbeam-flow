from collections import defaultdict

import bpy
from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from . import jbeam_utils
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
        print("Loading vehicle config '{}'".format(self.filename))
        with open(self.filepath, encoding='utf-8') as pc_file:
            jbeam_utils.VehicleBuilder.pc(self.filename, pc_file, context)
        try:
            pass
        except Exception as err:
            self.report({'ERROR'}, str(err))
            return {'CANCELLED'}

        return {'FINISHED'}


classes = (
    LoadVehicleConfig,
)
