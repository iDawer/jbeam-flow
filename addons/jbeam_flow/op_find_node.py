import bmesh
from bpy.props import StringProperty
from bpy.types import Operator

from . import bl_jbeam


class FindNode(Operator):
    bl_idname = "scene.jbeam_find_node"
    bl_label = "JBeam: Find node"
    bl_description = "Find jbeam node on the scene and place 3D Cursor"
    bl_options = {'REGISTER', 'UNDO'}

    node_id = StringProperty(
        name="Node ID",
        description="Jbeam node id to find",
    )

    def execute(self, context):
        node_id = self.node_id
        for obj in context.scene.objects:
            if obj.type != 'MESH':
                continue
            if obj.data.is_editmode:
                bm = bmesh.from_edit_mesh(obj.data)
            else:
                bm = bmesh.new()
                bm.from_mesh(obj.data)
            id_layer = bm.verts.layers.string.get(bl_jbeam.Node.id.layer_name)
            if id_layer is None:
                continue
            for vert in bm.verts:
                if vert[id_layer].decode() == node_id:
                    context.scene.cursor_location = vert.co
                    self.report({'INFO'}, "%s found in %s" % (node_id, obj.name))
                    return {'FINISHED'}

        self.report({'INFO'}, "%s not found" % node_id)
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


classes = (
    FindNode,
)
