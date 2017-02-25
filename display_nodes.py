import time

import bpy
import bgl
import blf
import bmesh
from bpy.props import BoolProperty
from bpy_extras.view3d_utils import location_3d_to_region_2d


def draw_ui(self, context):
    # context.mode == 'EDIT_MESH' cuz we are in the Mesh Display panel
    if context.active_object.type == 'MESH':
        layout = self.layout
        layout.label(text="Jbeam info:")

        row = layout.row(align=True)
        row.prop(context.active_object.data, 'show_jbeam_nodes', toggle=True)


class KotL:  # magic here!
    draw_nodes_handle = None
    drawing_mesh = None

    @staticmethod
    def start_draw(args):
        if KotL.draw_nodes_handle is not None:
            KotL.stop_it()
        KotL.draw_nodes_handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_nodes, args, 'WINDOW', 'POST_PIXEL')  # PRE_VIEW POST_VIEW POST_PIXEL
        KotL.drawing_mesh = args[0]

    @staticmethod
    def stop_it():
        bpy.types.SpaceView3D.draw_handler_remove(KotL.draw_nodes_handle, 'WINDOW')
        KotL.draw_nodes_handle = None


def update_show(self, context):
    print('update_show', time.time())
    if self.show_jbeam_nodes:
        KotL.start_draw((self, context))
    else:
        KotL.stop_it()


def draw_nodes(self, context):
    print('draw', time.time())
    obj = context.active_object
    if not obj.data.is_editmode:
        self.show_jbeam_nodes = False
        return

    bm = bmesh.from_edit_mesh(obj.data)
    id_layer = bm.verts.layers.string.get('jbeamNodeId')
    if id_layer is None:
        return

    obj_location = obj.location
    region = context.region
    rv3d = context.region_data

    font_id = 0
    blf.size(font_id, 13, 72)

    for vert in bm.verts:
        world_co = obj_location + vert.co
        co_2d = location_3d_to_region_2d(region, rv3d, world_co)
        if co_2d is None:
            # vert is behind the origin of a perspective view
            continue
        blf.position(font_id, co_2d.x, co_2d.y, 0)
        blf.draw(font_id, vert[id_layer].decode())

    blf.position(font_id, 1, 1, 0)
    blf.draw(font_id, "Hello Word ")

    # 50% alpha, 2 pixel width line
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 0.5)
    bgl.glLineWidth(2)

    bgl.glBegin(bgl.GL_LINE_STRIP)
    # for x, y in self.mouse_path:
    #     bgl.glVertex2i(x, y)

    bgl.glEnd()

    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)


def register():
    bpy.types.Mesh.show_jbeam_nodes = BoolProperty(
        name="Nodes",
        description="Display jbeam nodes id",
        update=update_show
    )
    bpy.types.VIEW3D_PT_view3d_meshdisplay.append(draw_ui)


def unregister():
    if KotL.drawing_mesh is not None:
        KotL.drawing_mesh.show_jbeam_nodes = False
    del bpy.types.Mesh.show_jbeam_nodes
    bpy.types.VIEW3D_PT_view3d_meshdisplay.remove(draw_ui)
