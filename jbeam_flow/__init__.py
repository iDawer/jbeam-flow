bl_info = {
    'name': 'BeamNG JBeam format',
    'author': 'Dawer',
    'location': 'File > Import > JBeam (.jbeam)',
    'category': 'Import-Export'
}

# To support reload properly, try to access a package var,
# if it's there, reload everything
is_reloading = "bpy" in locals()
import bpy
from . import (
    jb,
    jbeam,
    bl_jbeam,
    jbeam_utils,
    op_import,
    op_sync_to_jbeam,
    op_move_dummies,
    op_rename_node,
    display_nodes,
    props_inheritance,
    op_find_node,
    op_import_vehicle,
    op_load_vehicle_config,
)

if is_reloading:
    import importlib

    importlib.reload(jb)
    importlib.reload(jbeam)
    importlib.reload(bl_jbeam)
    importlib.reload(jbeam_utils)
    importlib.reload(op_import)
    importlib.reload(op_sync_to_jbeam)
    importlib.reload(op_move_dummies)
    importlib.reload(op_rename_node)
    importlib.reload(display_nodes)
    importlib.reload(props_inheritance)
    importlib.reload(op_find_node)
    importlib.reload(op_import_vehicle)
    importlib.reload(op_load_vehicle_config)
    print('Reloaded JBeam plugin')
else:
    print("Imported JBeam plugin")


#
#    Registration
#

def register():
    bpy.utils.register_module(__name__)
    display_nodes.register()
    bl_jbeam.register()
    print("REGISTERED  JBeam plugin")


def unregister():
    bpy.utils.unregister_module(__name__)
    display_nodes.unregister()
    bl_jbeam.unregister()
    print("UNREGISTERED  JBeam plugin")
