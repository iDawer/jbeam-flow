import bpy
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
import time
import bmesh
from antlr4 import *
from .jb import jbeamLexer, jbeamParser, jbeamVisitor
from . import jbeam_utils
from antlr4.IntervalSet import IntervalSet
from antlr4.TokenStreamRewriter import TokenStreamRewriter

use_profile = False


class SyncMeshToText(Operator):
    bl_idname = "mesh.sync_to_jbeam"
    bl_label = "JBeam live"
    bl_options = {'REGISTER', 'UNDO'}

    running = False

    def execute(self, context):
        if context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, 'only Edit mode')
            return {'CANCELLED'}

        text_datablock = bpy.data.texts['van_cargobase_mod.jbeam']
        data = text_datablock.as_string()
        data_stream = InputStream(data)

        lexer = jbeamLexer(data_stream)
        stream = CommonTokenStream(lexer)
        parser = jbeamParser(stream)
        tree = parser.jbeam()
        rewriter = TokenStreamRewriter(stream)

        collector = jbeam_utils.NodeCollector('van_cargobase_mod')
        collector.visit(tree)

        bm = bmesh.from_edit_mesh(context.active_object.data)
        id_lyr = bm.verts.layers.string['jbeamNodeId']
        for vert in bm.verts:
            _id = vert[id_lyr].decode()
            x = round(vert.co.x, 3)
            y = round(vert.co.y, 3)
            z = round(vert.co.z, 3)
            node = collector.nodes[_id]
            rewriter.replaceSingleToken(node.posX, str(x))
            rewriter.replaceSingleToken(node.posY, str(y))
            rewriter.replaceSingleToken(node.posZ, str(z))

        new_str = rewriter.getText()
        text_datablock.clear()
        text_datablock.write(new_str)

        return {'FINISHED'}

    # Profiling dance
    if use_profile:
        _execute = execute

        def execute(self, context):
            import cProfile, time
            profiler = cProfile.Profile()
            profiler.enable()
            result = None
            try:
                result = self._execute(context)
            except:
                raise  # bubble up to the UI
            finally:
                profiler.disable()
                profiler.dump_stats(
                    r'C:\\Users\\Dawer\\AppData\\Roaming\\Blender '
                    r'Foundation\\Blender\\2.78\\scripts\\addons\\BlenderJBeam\\profile\\LiveEditor{0}.pstat'.format(
                        str(time.time())))
                return result


    # def modal(self, context, event):
    #     print('\r', time.time(), end='')
    #     if context.active_object.is_updated:
    #         print('\nis_updated')
    #
    #     if LiveEditor.running:
    #         return {"PASS_THROUGH"}
    #     else:
    #         return {"CANCELLED"}

    # def invoke(self, context, event):
    #     print('invoke')
    #     if LiveEditor.running:
    #         LiveEditor.running = False
    #         return {"CANCELLED"}
    #     else:
    #         LiveEditor.running = True
    #         # context.window_manager.modal_handler_add(self)
    #         return {'RUNNING_MODAL'}

    # @staticmethod
    # def register():
    #     bpy.types.INFO_MT_file_import.append(menu_func_draw)
    #
    # @staticmethod
    # def unregister():
    #     bpy.types.INFO_MT_file_import.remove(menu_func_draw)
    #
