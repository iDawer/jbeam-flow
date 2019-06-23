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
    """Unused, obsolete. See :class:`bl_jbeam.RNAProxyMeta`"""

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
        p_node = edit_mesh.jbeam_pgeometry.nodes.proxy_active

        if p_node is None:
            self.layout.label("No active node.")
            return

        self.layout.prop(p_node, 'id')

        self.layout.label("Private properties:")
        row = self.layout.row(align=True)
        row.prop(p_node, 'props_src', text="")
        op_props = row.operator(text_prop_editor.EditOperator.bl_idname, text="",
                                icon='TEXT')  # type: text_prop_editor.EditOperator
        op_props.settings.full_data_path = repr(p_node)
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
        layout = self.layout
        edit_mesh = context.edit_object.data  # type: bpy.types.Mesh
        p_beam = edit_mesh.jbeam_pgeometry.beams.proxy_active

        if p_beam is None:
            layout.label("No active edge")
            return
        layout.prop(p_beam, 'name')
        # layout.label(p_beam.name)
        layout.prop(p_beam, 'is_ghost')

        if not p_beam.is_ghost:
            layout.label("Private properties:")
            row = layout.row(align=True)
            row.prop(p_beam, 'props_src', text="")
            op_props = row.operator(text_prop_editor.EditOperator.bl_idname, text="",
                                    icon='TEXT')  # type: text_prop_editor.EditOperator
            op_props.settings.full_data_path = repr(p_beam)
            op_props.settings.attr = 'props_src'
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
        layout = self.layout
        edit_mesh = context.edit_object.data  # type: bpy.types.Mesh
        p_surf = edit_mesh.jbeam_pgeometry.proxy_active_surface

        if p_surf is None:
            layout.label("No active face")
            return

        with Switch(p_surf.vertices) as case:
            if case(3):
                layout.label("Triangle")
            elif case(4):
                layout.label("Quad")
            else:
                # todo: explain to user why error icon is there
                layout.label("Polygon", icon='ERROR')

        layout.prop(p_surf, 'name')

        layout.label("Private properties:")
        row = layout.row(align=True)
        row.prop(p_surf, 'props_src', text="")
        op_props = row.operator(text_prop_editor.EditOperator.bl_idname, text="",
                                icon='TEXT')  # type: text_prop_editor.EditOperator
        op_props.settings.full_data_path = repr(p_surf)
        op_props.settings.attr = 'props_src'
        op_props.settings.apply_text = "Apply to active surface"


classes = (
    ProxyGroup,
    JbeamNodeEditPanel,
    JbeamBeamEditPanel,
    JbeamSurfaceEditPanel,
)
