import bmesh
import bpy
from bpy.props import StringProperty, PointerProperty, BoolProperty

from . import (
    bl_jbeam,
    bm_props,
    text_prop_editor,
)
from .jbeam.misc import Switch


class ProxyGroup(bpy.types.PropertyGroup):
    node_id = bm_props.make_rna_proxy(
        bl_jbeam.Node,
        bl_jbeam.Node.id,
        StringProperty(name="Node id", options={'TEXTEDIT_UPDATE'},
                       description="Name of the node. '~' at start means it is dummy copy from parent part"))
    node_private_props = bm_props.make_rna_proxy(
        bl_jbeam.Node,
        bl_jbeam.Node.props_src,
        StringProperty(name="Private properties"))

    beam_is_ghost = bm_props.make_rna_proxy(
        bl_jbeam.Beam,
        bl_jbeam.Beam.is_ghost,
        BoolProperty(name="Ghost", description="Ghost beams will not export. "
                                               "Useful for triangles with edges which are not defined as beams."))
    beam_private_props = bm_props.make_rna_proxy(
        bl_jbeam.Beam,
        bl_jbeam.Beam.props_src,
        StringProperty(name="Private properties"))

    surface_private_props = bm_props.make_rna_proxy(
        bl_jbeam.Surface,
        bl_jbeam.Surface.props_src,
        StringProperty(name="Private properties")
    )

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
        edit_mesh = context.edit_object.data  # type: bpy.types.Mesh
        active_node = edit_mesh.jbeam_pgeometry.nodes.proxy_active

        if active_node is None:
            self.layout.label("No active node.")
            return

        self.layout.prop(active_node, 'id')

        self.layout.label("Private properties:")
        row = self.layout.row(align=True)
        row.prop(active_node, 'props_src', text="")
        op_props = row.operator(text_prop_editor.EditOperator.bl_idname, text="",
                                icon='TEXT')  # type: text_prop_editor.EditOperator
        op_props.settings.full_data_path = repr(active_node)
        op_props.settings.attr = 'props_src'
        op_props.settings.apply_text = "Apply to active node"


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
        if edge is None or not isinstance(edge, bmesh.types.BMEdge):
            self.layout.row().label("No active edge")
            return
        beam = bl_jbeam.Beam(bm, edge)
        self.layout.label(str(beam))

        lyr = bl_jbeam.Beam.is_ghost.get_layer(bm.edges.layers)
        if lyr is None:
            self.layout.row().label("No 'is_ghost' data layer")
        else:
            self.layout.prop(context.window_manager.jbeam_flow_proxies, "beam_is_ghost")

        props_lyr = bl_jbeam.Beam.props_src.get_layer(bm.edges.layers)
        if props_lyr is None:
            self.layout.row().label("No properties data layer")
        else:
            self.layout.label("Private properties:")
            row = self.layout.row(align=True)
            row.prop(context.window_manager.jbeam_flow_proxies, 'beam_private_props', text="")
            op_props = row.operator(text_prop_editor.EditOperator.bl_idname, text="",
                                    icon='TEXT')  # type: text_prop_editor.EditOperator
            op_props.settings.full_data_path = repr(context.window_manager.jbeam_flow_proxies)
            op_props.settings.attr = 'beam_private_props'
            op_props.settings.apply_text = "Apply to active beam"


class JbeamSurfaceEditPanel(bpy.types.Panel):
    bl_label = "JBeam Surface"
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D"

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.object is not None and context.object.type == "MESH" \
               and context.tool_settings.mesh_select_mode[2]

    def draw(self, context: bpy.types.Context):
        obj = context.object
        bm = bmesh.from_edit_mesh(obj.data)
        active_element = bm.select_history.active
        if active_element is None or not isinstance(active_element, bmesh.types.BMFace):
            self.layout.row().label("No active face")
            return

        with Switch(len(active_element.verts)) as case:
            if case(3):
                self.layout.label("Triangle")
            elif case(4):
                self.layout.label("Quad")
            else:
                self.layout.label("Polygon", icon='ERROR')

        props_lyr = bl_jbeam.Surface.props_src.get_layer(bm.edges.layers)
        if props_lyr is None:
            self.layout.row().label("No properties data layer")
        else:
            self.layout.label("Private properties:")
            row = self.layout.row(align=True)
            row.prop(context.window_manager.jbeam_flow_proxies, 'surface_private_props', text="")
            op_props = row.operator(text_prop_editor.EditOperator.bl_idname, text="",
                                    icon='TEXT')  # type: text_prop_editor.EditOperator
            op_props.settings.full_data_path = repr(context.window_manager.jbeam_flow_proxies)
            op_props.settings.attr = 'surface_private_props'
            op_props.settings.apply_text = "Apply to active surface"


classes = (
    ProxyGroup,
    JbeamNodeEditPanel,
    JbeamBeamEditPanel,
    JbeamSurfaceEditPanel,
)
