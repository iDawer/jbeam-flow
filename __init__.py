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

    importlib.reload(jbeam_utils)
    importlib.reload(op_import)
    print('Reloaded JBeam plugin')
else:
    import bpy
    from . import (
        jbeam_utils,
        op_import
    )

    print("Imported JBeam plugin")


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
