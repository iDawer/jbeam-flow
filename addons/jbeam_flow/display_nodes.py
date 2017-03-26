import time

import bpy
import bgl
import blf
import bmesh
from bpy.props import BoolProperty
from bpy_extras.view3d_utils import location_3d_to_region_2d


def draw_ui_mesh_display(self, context):
    if context.active_object.type == 'MESH':
        layout = self.layout
        layout.label(text="Jbeam info:")

        row = layout.row(align=True)
        row.prop(context.active_object, 'show_jbeam_nodes')


def draw_ui_display(self, context):
    layout = self.layout
    layout.label(text="Jbeam info:")

    row = layout.row(align=True)
    row.prop(context.scene, 'show_all_jbeam_nodes')


class KotL:  # magic here!
    draw_nodes_handle = None

    @staticmethod
    def start_draw(args: tuple):
        if KotL.draw_nodes_handle is not None:
            KotL.stop_it()
        KotL.draw_nodes_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_nodes, args, 'WINDOW', 'POST_PIXEL')  # PRE_VIEW POST_VIEW POST_PIXEL

    @staticmethod
    def stop_it():
        bpy.types.SpaceView3D.draw_handler_remove(KotL.draw_nodes_handle, 'WINDOW')
        KotL.draw_nodes_handle = None


def draw_nodes():
    # enter_time = time.time()
    # i = 0

    context = bpy.context
    for obj in context.visible_objects:
        if obj.type != 'MESH' or not (context.scene.show_all_jbeam_nodes or obj.show_jbeam_nodes):
            continue

        if obj.data.is_editmode:
            bm = bmesh.from_edit_mesh(obj.data)
        else:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
        id_layer = bm.verts.layers.string.get('jbeamNodeId')
        if id_layer is None:
            continue

        obj_matrix = obj.matrix_world
        region = context.region
        rv3d = context.region_data

        font_id = 0
        bgl.glColor3f(1.0, 1.0, 1.0)
        blf.size(font_id, 13, 72)

        for vert in bm.verts:
            world_co = obj_matrix * vert.co
            co_2d = location_3d_to_region_2d(region, rv3d, world_co)
            if co_2d is None:
                # vert is behind the origin of a perspective view
                continue
            blf.position(font_id, co_2d.x + 3, co_2d.y, 0)
            blf.draw(font_id, vert[id_layer].decode())
            # i += 1

    pass
    # print(i, 'nodes drawn in', time.time() - enter_time)


def register():
    bpy.types.Object.show_jbeam_nodes = BoolProperty(
        name="Nodes",
        description="Display jbeam nodes id",
        options={'HIDDEN'},
    )
    bpy.types.Scene.show_all_jbeam_nodes = BoolProperty(
        name="All nodes",
        description="Force display all jbeam nodes id",
        options={'HIDDEN'},
    )
    bpy.types.VIEW3D_PT_view3d_meshdisplay.append(draw_ui_mesh_display)
    bpy.types.OBJECT_PT_display.append(draw_ui_mesh_display)
    bpy.types.VIEW3D_PT_view3d_display.append(draw_ui_display)
    KotL.start_draw(())


def unregister():
    KotL.stop_it()
    del bpy.types.Object.show_jbeam_nodes
    del bpy.types.Scene.show_all_jbeam_nodes
    bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(draw_ui_mesh_display)
    bpy.types.OBJECT_PT_display.remove(draw_ui_mesh_display)
    bpy.types.VIEW3D_PT_view3d_display.remove(draw_ui_display)
