import bmesh
import bpy
from bpy.props import StringProperty, PointerProperty, BoolProperty

from . import bl_jbeam, bm_props


class ProxyGroup(bpy.types.PropertyGroup):
    node_id = bm_props.make_rna_proxy(
        bl_jbeam.Node,
        bl_jbeam.Node.id,
        StringProperty(name="Node id", options={'TEXTEDIT_UPDATE'}))
    node_prop_src = bm_props.make_rna_proxy(
        bl_jbeam.Node,
        bl_jbeam.Node.props_src,
        StringProperty(name="Private properties"))

    beam_is_ghost = bm_props.make_rna_proxy(
        bl_jbeam.Beam,
        bl_jbeam.Beam.is_ghost,
        BoolProperty(name="Ghost", description="Ghost beams are not exported. "
                                               "Useful for triangles with edges which are not defined as beams."))
    beam_prop_src = bm_props.make_rna_proxy(
        bl_jbeam.Beam,
        bl_jbeam.Beam.props_src,
        StringProperty(name="Private properties"))

    @classmethod
    def register(cls):
        bpy.types.WindowManager.jbeam_flow_proxies = PointerProperty(type=cls, options={'SKIP_SAVE'})

    @classmethod
    def unregister(cls):
        del bpy.types.WindowManager.jbeam_flow_proxies


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
        if v is None:
            self.layout.row().label("No active node")
            return

        id_lyr = bl_jbeam.Node.id.get_layer(bm.verts.layers)
        if id_lyr is None:
            self.layout.row().label("No id data layer")
        else:
            self.layout.prop(context.window_manager.jbeam_flow_proxies, "node_id")

        props_lyr = bl_jbeam.Node.props_src.get_layer(bm.verts.layers)
        if props_lyr is None:
            self.layout.row().label("No properties data layer")
        else:
            self.layout.prop(context.window_manager.jbeam_flow_proxies, "node_prop_src")


class JbeamBeamEditPanel(bpy.types.Panel):
    bl_label = "JBeam Beam"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.object is not None and context.object.type == "MESH" \
               and context.tool_settings.mesh_select_mode[1]  # edges select mode

    def draw(self, context: bpy.types.Context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        edge = bm.select_history.active
        if edge is None:
            self.layout.row().label("No active edge")
            return

        lyr = bl_jbeam.Beam.is_ghost.get_layer(bm.edges.layers)
        if lyr is None:
            self.layout.row().label("No 'is_ghost' data layer")
        else:
            self.layout.prop(context.window_manager.jbeam_flow_proxies, "beam_is_ghost")

        props_lyr = bl_jbeam.Beam.props_src.get_layer(bm.edges.layers)
        if props_lyr is None:
            self.layout.row().label("No properties data layer")
        else:
            self.layout.prop(context.window_manager.jbeam_flow_proxies, "beam_prop_src")


classes = (
    ProxyGroup,
    JbeamNodeEditPanel,
    JbeamBeamEditPanel,
)
