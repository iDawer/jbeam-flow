bl_info = {
    'name': 'BeamNG JBeam format',
    'author': 'Dawer',
    'location': 'File > Import > JBeam (.jbeam)',
    'category': 'Import-Export'
}

# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "bpy" in locals():
    import importlib

    importlib.reload(importJBeam)
    print('Reloaded JBeam plugin')
else:
    from . import jbeam_utils

    # import operator_file_import
    print("Imported JBeam plugin")

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ImportSomeData(Operator, ImportHelper):
    """Import from BeamNG's JBeam file"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import JBeam"

    # ImportHelper mixin class uses this
    filename_ext = ".jbeam"

    filter_glob = StringProperty(
        default="*.jbeam",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    use_setting = BoolProperty(
        name="Example Boolean",
        description="Example Tooltip",
        default=True,
    )

    type = EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(('OPT_A', "First Option", "Description one"),
               ('OPT_B', "Second Option", "Description two")),
        default='OPT_A',
    )

    def execute(self, context):
        from . import jbeam_utils
        return jbeam_utils.read_some_data(context, self.filepath, self.use_setting)

    @staticmethod
    def register():
        bpy.types.INFO_MT_file_import.append(menu_func_draw)

    @staticmethod
    def unregister():
        bpy.types.INFO_MT_file_import.remove(menu_func_draw)


# Only needed if you want to add into a dynamic menu
def menu_func_draw(self, context):
    self.layout.operator(ImportSomeData.bl_idname, text="JBeam (.jbeam)")


#
#    Registration
#

def register():
    bpy.utils.register_module(__name__)
    print("REGISTERED  JBeam plugin")


def unregister():
    bpy.utils.unregister_module(__name__)
    print("UNREGISTERED  JBeam plugin")


if __name__ == "__main__":
    register()
