import bmesh
import bpy
from bpy.props import StringProperty

from . import bl_jbeam, bm_props


class JbeamNodeEditPanel(bpy.types.Panel):
    bl_label = "JBeam Node"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.object is not None and context.object.type == "MESH" \
               and context.tool_settings.mesh_select_mode[0]  # verts select mode

    def draw(self, context: bpy.types.Context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        v = bm.select_history.active
        id_lyr = bl_jbeam.Node.id.get_layer(bm.verts.layers)
        if id_lyr is None:
            self.layout.row().label("No id data layer")
        elif v is None:
            self.layout.row().label("No active node")
        else:
            self.layout.prop(context.window_manager, "proxy_jbeam_node_id")
        props_lyr = bl_jbeam.Node.props_src.get_layer(bm.verts.layers)
        if props_lyr is None:
            self.layout.row().label("No properties data layer")
        elif v is None:
            pass
        else:
            self.layout.prop(context.window_manager, "proxy_jbeam_node_prop_src")

    @classmethod
    def register(cls):
        bpy.types.WindowManager.proxy_jbeam_node_id = bm_props.make_rna_proxy(
            bl_jbeam.Node.id,
            StringProperty(name="Node id", options={'TEXTEDIT_UPDATE'}),
            bmesh.types.BMesh.verts,
            bmesh.types.BMVert)
        bpy.types.WindowManager.proxy_jbeam_node_prop_src = bm_props.make_rna_proxy(
            bl_jbeam.Node.props_src,
            StringProperty(name="Private properties"),
            bmesh.types.BMesh.verts,
            bmesh.types.BMVert)

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.proxy_jbeam_node_id
        del bpy.types.WindowManager.proxy_jbeam_node_prop_src
