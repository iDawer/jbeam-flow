import bmesh
import bpy
from bpy.props import BoolProperty
from bpy.types import Operator

from . import bl_jbeam
from .jbeam.misc import anytree


class MoveDummies(Operator):
    bl_idname = "scene.jbeam_adjust_dummies"
    bl_label = "JBeam: Move dummy nodes to position of their originals"
    bl_options = {'REGISTER', 'UNDO'}

    all_scene_objects = BoolProperty(
        name="Whole scene",
        description="Perform adjusting for whole scene or active object only",
        default=True,
    )

    def execute(self, context):

        # slot_node = build_tree_with(context.scene.objects, active_obj.parent)
        # root = slot_node.root
        # # tree walking iterator
        # nodes_iter = anytree.PreOrderIter(root)

        # collect all jnode ids and coordinates in the object hierarchy
        jnode_map = {}
        for ob in context.scene.objects:
            if ob.type == 'MESH':
                # note jnode id can be overwritten during dic.update(), i.e. part's jnode overrides parent's node!
                # Is this behavior correct? ToDo check jnode override behavior
                jnode_map.update(get_jnodes_co(ob))

        print("Adjusting dummy nodes position...")
        overall_result = 0, 0
        if self.all_scene_objects:
            for ob in context.scene.objects:
                if ob.type == 'MESH':
                    result = position_dummies(jnode_map, ob)
                    overall_result = vector_sum(overall_result, result)
        else:
            active_obj = context.active_object
            if not active_obj:
                self.report({'ERROR'}, "Select a part")
                return {'CANCELLED'}
            if active_obj.type != 'MESH':
                self.report({'ERROR_INVALID_INPUT'}, "Mesh type object required")
                return {'CANCELLED'}
            if active_obj.parent is None:
                self.report({'ERROR_INVALID_INPUT'}, "Active object is not parented")
                return {'CANCELLED'}
            overall_result = position_dummies(jnode_map, active_obj)

        rtype = {'WARNING'} if overall_result[1] else {'INFO'}
        self.report(rtype, "Adjusted %d dummies, unbound %d. See console for details" % overall_result)

        return {'FINISHED'}

    pass


def get_jnodes_co(obj):
    mtx_to_world = obj.matrix_world
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    id_lyr = bm.verts.layers.string.get(bl_jbeam.Node.id.layer_name)
    if id_lyr is None:
        return
    for v in bm.verts:
        _id = v[id_lyr].decode()  # decode byte array
        if _id:
            # jnode id is not None and not empty
            yield _id, mtx_to_world * v.co.copy()


def position_dummies(jnode_map, obj):
    me = obj.data
    print("\t{:40}|".format(me.name), end=" ")
    if me.is_editmode:
        bm = bmesh.from_edit_mesh(me)
    else:
        bm = bmesh.new()
        bm.from_mesh(me)

    id_lyr = bm.verts.layers.string.get(bl_jbeam.Node.id.layer_name)
    if not id_lyr:
        print('No id data')
        return 0, 0

    dummy_verts = {_id.lstrip('~'): v for _id, v in ((v[id_lyr].decode(), v) for v in bm.verts)
                   if _id and _id.startswith('~')}

    mtx_w_to_local = obj.matrix_world.inverted()
    reals_found = []
    for _id, dummy_v in dummy_verts.items():
        real_co = jnode_map.get(_id, None)
        if real_co:
            dummy_v.co = mtx_w_to_local * real_co
            reals_found.append(_id)

    for _id in reals_found:
        dummy_verts.pop(_id)

    if me.is_editmode:
        bmesh.update_edit_mesh(me, destructive=False)
    else:
        bm.to_mesh(me)
    me.update()

    if dummy_verts:
        print("Unbound dummies: ", ', '.join(('~' + _id for _id in sorted(dummy_verts))))
    else:
        print("ok")

    return len(reals_found), len(dummy_verts)


def build_tree_with(obj_map, specific_obj):
    node_map = {obj.name: Node(obj.name, obj=obj) for obj in obj_map}
    for name, node in node_map.items():
        if node.obj.parent is not None:
            parent_node = node_map.get(node.obj.parent.name, None)
            if parent_node is not None:
                # is parent linked to the scene?
                node.parent = parent_node

    roots = (node for node in node_map.values() if node.is_root)

    text = bpy.data.texts.get('tree') or bpy.data.texts.new('tree')
    text.clear()
    for rot in roots:
        text.write(str(anytree.RenderTree(rot)) + '\n')

    spec_node = node_map[specific_obj.name]
    return spec_node


def vector_sum(t1, t2):
    return tuple(p + q for p, q in zip(t1, t2))


class Node(anytree.Node):
    """Tree node, simple repr()"""

    def __repr__(self):
        return self.name
