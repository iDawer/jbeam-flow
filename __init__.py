bl_info = {
    'name': 'BeamNG JBeam format',
    'author': 'Dawer',
    'location': 'File > Import > JBeam (.jbeam)',
    'category': 'Import-Export'
}


class reloadable:
    """ Utility class that helps with reloading submodules imported with from..import statement.
     'import bpy' should be inside 'with' block to determine reloading. """

    def __init__(self, mod_name, mod_locals):
        self.mod_name = mod_name
        # To support reload properly, try to access a package var, if it's there, reload everything
        self.is_reloading = 'bpy' in mod_locals
        self.modules = []
        """List of loaded modules. Preserves importing order"""

    def __enter__(self):
        import builtins
        original_import = self.original_import = builtins.__import__
        mod_name = self.mod_name
        self.modules = []

        def hook_import(name, globals_=None, locals_=None, fromlist=(), level=0):
            mod = original_import(name, globals=globals_, locals=locals_, fromlist=fromlist, level=level)
            if globals_ and globals_['__name__'] == mod_name:
                if fromlist:
                    self.modules.extend((getattr(mod, submod_name) for submod_name in fromlist))
            return mod

        builtins.__import__ = hook_import
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        import builtins
        builtins.__import__ = self.original_import
        if self.is_reloading:
            from importlib import reload
            self.modules = [reload(mod) for mod in self.modules]
            print("Reloaded submodules of '{}'".format(self.mod_name))
            del reload
        else:
            print("Imported submodules of '{}'".format(self.mod_name))
        return False


with reloadable(__name__, locals()) as loaded:
    import bpy
    from . import (
        bm_props,
        jbeam,
        bl_jbeam,
        jbeam_utils,
        text_prop_editor,
        op_import,
        op_fill_slots,
        op_move_dummies,
        op_rename_node,
        display_nodes,
        ui_part,
        props_inheritance,
        op_find_node,
        op_import_vehicle,
        op_load_vehicle_config,
        jbeam_elem_editor,
    )


def register():
    from bpy.utils import register_class
    for cls in (cls for mod in loaded.modules for cls in mod.classes):
        register_class(cls)
    del register_class
    display_nodes.register()
    print("REGISTERED '{}'".format(__name__))


def unregister():
    from bpy.utils import unregister_class
    for cls in reversed([cls for mod in loaded.modules for cls in mod.classes]):
        unregister_class(cls)
    del unregister_class
    display_nodes.unregister()
    print("UNREGISTERED  '{}'".format(__name__))
