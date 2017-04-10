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
        # To support reload properly, try to access a package var,
        # if it's there, reload everything
        self.is_reloading = 'bpy' in mod_locals
        self.modules = []

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


def register():
    bpy.utils.register_module(__name__)
    for submodule in loaded.modules:
        # Allow explicit registering methods in a submodules
        if hasattr(submodule, 'register'):
            submodule.register()
    print("REGISTERED '{}'".format(__name__))


def unregister():
    bpy.utils.unregister_module(__name__)
    for submodule in loaded.modules:
        if hasattr(submodule, 'unregister'):
            submodule.unregister()
    print("UNREGISTERED  '{}'".format(__name__))
