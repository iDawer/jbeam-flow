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

    importlib.reload(jb)
    importlib.reload(misc)
    importlib.reload(jbeam_utils)
    importlib.reload(op_import)
    importlib.reload(op_sync_to_jbeam)
    importlib.reload(op_move_dummies)
    importlib.reload(op_rename_node)
    importlib.reload(display_nodes)
    importlib.reload(props_inheritance)
    print('Reloaded JBeam plugin')
else:
    import bpy
    from . import (
        jb,
        misc,
        jbeam_utils,
        op_import,
        op_sync_to_jbeam,
        op_move_dummies,
        op_rename_node,
        display_nodes,
        props_inheritance,
    )

    print("Imported JBeam plugin")


#
#    Registration
#

def register():
    bpy.utils.register_module(__name__)
    display_nodes.register()
    print("REGISTERED  JBeam plugin")


def unregister():
    bpy.utils.unregister_module(__name__)
    display_nodes.unregister()
    print("UNREGISTERED  JBeam plugin")
