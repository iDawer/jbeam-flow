import bmesh
from bpy.props import StringProperty
from bpy.types import Operator


class Rename(Operator):
    bl_idname = "object.jbeam_rename_node"
    bl_label = "Rename node"
    bl_description = "Renames jbeam node"
    bl_options = {'REGISTER', 'UNDO'}

    node_id = StringProperty(
        name="Node ID",
        description="Jbeam node id",
        options={'TEXTEDIT_UPDATE'}
    )

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.data.is_editmode

    def execute(self, context):
        obj = context.active_object
        if obj is None or not obj.data.is_editmode:
            self.report({'ERROR'}, 'cancelled')
            return {'CANCELLED'}

        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        id_lyr = bm.verts.layers.string['jbeamNodeId']
        for vert in bm.verts:
            if vert.select:
                vert[id_lyr] = self.node_id.encode()
                break
        return {'FINISHED'}

    def invoke(self, context, event):
        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        id_lyr = bm.verts.layers.string.get('jbeamNodeId')

        if id_lyr is None:
            self.report({'ERROR_INVALID_INPUT'}, 'Mesh has no jbeam data')
            return {'CANCELLED'}

        for vert in bm.verts:
            if vert.select:
                self.node_id = vert[id_lyr].decode()
                break

        return {'FINISHED'}
