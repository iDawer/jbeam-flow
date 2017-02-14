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
    bl_label = "Sync mesh to jbeam"
    bl_options = {'REGISTER', 'UNDO'}

    running = False

    def execute(self, context):
        obj = context.active_object
        if obj.data.is_editmode:
            bm = bmesh.from_edit_mesh(obj.data)
        else:
            bm = bmesh.new()
            bm.from_mesh(obj.data)

        # ToDo handle multiple groups.
        # Find first corresponding jbeam name stored in the group's custom property 'jbeam_textblock'.
        # Remember that group['jbeam_textblock'] == Text.name
        text_dblock_name = next(
            (jb for jb in (group.get('jbeam_textblock') for group in obj.users_group) if jb is not None), None)
        if text_dblock_name is None:
            self.report({'ERROR_INVALID_INPUT'}, 'Corresponding jbeam group is not found')
            return {'CANCELLED'}

        part_name = obj.data.get('jbeam_part')
        if part_name is None:
            self.report({'ERROR_INVALID_INPUT'},
                        "Missing property: {0} has no custom property 'jbeam_part'".format(obj.data))
            return {'CANCELLED'}

        text_datablock = bpy.data.texts[text_dblock_name]
        data = text_datablock.as_string()

        tree = jbeam_utils.get_parse_tree(data, text_dblock_name)
        stream = tree.parser.getTokenStream()
        rewriter = jbeam_utils.Rewriter(stream)

        part = jbeam_utils.NodeCollector(part_name)
        part.visit(tree)

        id_lyr = bm.verts.layers.string['jbeamNodeId']
        nodes_to_del = part.nodes.copy()
        # update vert coordinates
        for vert in bm.verts:
            _id = vert[id_lyr].decode()
            if len(_id) == 0:  # ignore if no id set
                continue
            x = round(vert.co.x, 3)
            y = round(vert.co.y, 3)
            z = round(vert.co.z, 3)
            node = nodes_to_del.pop(_id)
            rewriter.replaceSingleToken(node.posX, str(x))
            rewriter.replaceSingleToken(node.posY, str(y))
            rewriter.replaceSingleToken(node.posZ, str(z))

        # rest nodes are not in the mesh, delete them
        for _id, node in nodes_to_del.items():
            rewriter.delete_subtree(node)
            # delete linked beams and tris
            for beam in part.node_to_items_map[_id]:
                rewriter.delete_subtree(beam)

        # process edges
        for edge in bm.edges:
            v1, v2 = edge.verts
            id1 = v1[id_lyr].decode()
            id2 = v2[id_lyr].decode()
            if len(id1) == 0 or len(id2) == 0:
                continue
            # just extract actual beam from part.beams
            beam = part.beams.pop(frozenset((id1, id2)), None)
            if beam is None:
                # we have no corresponding beam, so this edge is new
                continue  # just pass trough
        # rip remaining beams
        nodes_id_set = part.nodes.keys()
        for (id1, id2), beam in part.beams.items():
            # whoops, don't remove beams with external nodes
            if id1 in nodes_id_set and id2 in nodes_id_set:
                rewriter.delete_subtree(beam)

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
            try:
                result = self._execute(context)
            except:
                raise  # bubble up to the UI
            else:
                return result
            finally:
                profiler.disable()
                profiler.dump_stats(
                    r'C:\\Users\\Dawer\\AppData\\Roaming\\Blender '
                    r'Foundation\\Blender\\2.78\\scripts\\addons\\BlenderJBeam\\profile\\LiveEditor{0}.pstat'.format(
                        str(time.time())))


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
