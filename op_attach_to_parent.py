import bpy
import bmesh
from bpy.types import Operator


class AttachToParent(Operator):
    bl_idname = "object.jbeam_attach_to_parent"
    bl_label = "JBeam: Attach to parent"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        # ToDo check context and handle noninitialised data layers

        if not obj:
            self.report({'ERROR'}, 'There is no active object')
            return {'CANCELLED'}
        if obj.type != 'MESH':
            self.report({'ERROR_INVALID_INPUT'}, 'Mesh type object required')
            return {'CANCELLED'}
        if obj.parent is None:
            self.report({'ERROR_INVALID_INPUT'}, 'Active object is not parented')
            return {'CANCELLED'}

        me = obj.data
        if me.is_editmode:
            bm = bmesh.from_edit_mesh(me)
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

        id_lyr = bm.verts.layers.string['jbeamNodeId']
        dummy_verts = {_id.lstrip('~'): v for _id, v in ((v[id_lyr].decode(), v) for v in bm.verts)
                       if _id and _id.startswith('~')}

        if not dummy_verts:
            self.report({'INFO'}, 'Dummies are not found')
            return {'FINISHED'}

        position_dummies(dummy_verts, obj.parent)

        if dummy_verts:
            self.report({'WARNING'}, 'Not all dummies positioned, dumped to the console.')
            print('Not positioned dummies: ', ', '.join(('~' + _id for _id in sorted(dummy_verts))))
        else:
            self.report({'INFO'}, 'All dummies positioned')

        if me.is_editmode:
            bmesh.update_edit_mesh(me, destructive=False)
        else:
            bm.to_mesh(me)
        me.update()
        return {'FINISHED'}

    pass


def position_dummies(dummy_verts, parent):
    """Visit parents recursively and position dummies to their reals.
    After return dummy_verts contains dummies whose reals was not found"""
    if dummy_verts:
        if parent.type == 'MESH':
            bm_parent = bmesh.new()
            bm_parent.from_mesh(parent.data)
            pid_lyr = bm_parent.verts.layers.string['jbeamNodeId']
            for v in bm_parent.verts:
                _id = v[pid_lyr].decode()
                if _id:
                    dummy_v = dummy_verts.pop(_id, None)
                    if dummy_v:
                        dummy_v.co = v.co.copy()
        if parent.parent:
            position_dummies(dummy_verts, parent.parent)
