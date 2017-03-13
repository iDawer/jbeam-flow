import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
import cProfile


class ImportJBeam(Operator, ImportHelper):
    """Import from BeamNG's JBeam file"""
    bl_idname = "import_mesh.jbeam"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import JBeam (.jbeam)"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".jbeam"

    filter_glob = StringProperty(
        default="*.jbeam",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    filename = StringProperty(
        name="File Name",
        description="Filename used for importing the file",
        maxlen=255,
        subtype='FILE_NAME',
    )

    # # List of operator properties, the attributes will be assigned
    # # to the class instance from the operator settings before calling.
    # use_setting = BoolProperty(
    #     name="Example Boolean",
    #     description="Example Tooltip",
    #     default=True,
    # )
    #
    # type = EnumProperty(
    #     name="Example Enum",
    #     description="Choose between two items",
    #     items=(('OPT_A', "First Option", "Description one"),
    #            ('OPT_B', "Second Option", "Description two")),
    #     default='OPT_A',
    # )

    def execute(self, context):
        # profiler = cProfile.Profile()
        # profiler.enable()
        from . import jbeam_utils
        from .ext_json import decoder
        print("File:", self.filename)
        with open(self.filepath, encoding='utf-8') as file:
            content = file.read()

        tree = decoder.get_parse_tree(content)

        builder = jbeam_utils.PartObjectsBuilder(self.filename)
        builder.console_indent = 1
        builder.jbeam(tree)

        for obj in builder.get_all_objects():
            context.scene.objects.link(obj)

        # profiler.disable()
        # profiler.dump_stats(r'C:\Users\Dawer\AppData\Roaming\Blender '
        #                     r'Foundation\Blender\2.78\scripts\addons\BlenderJBeam\profile\ImportJBeam.pstat')
        # profiler.clear()

        return {'FINISHED'}

    @staticmethod
    def register():
        bpy.types.INFO_MT_file_import.append(menu_func_draw)

    @staticmethod
    def unregister():
        bpy.types.INFO_MT_file_import.remove(menu_func_draw)


def menu_func_draw(self, context):
    self.layout.operator(ImportJBeam.bl_idname)
