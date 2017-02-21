import bpy
import bmesh
from bpy.types import Operator

from .misc import anytree
from .misc.op_constants import opt, rep, ret


class AttachToParent(Operator):
    bl_idname = "object.jbeam_attach_to_parent"
    bl_label = "JBeam: Attach to parent"
    bl_options = {opt.REGISTER, opt.UNDO}

    def execute(self, context):
        obj = context.active_object
        # ToDo check context and handle noninitialised data layers

        if not obj:
            self.report({rep.ERROR}, 'There is no active object')
            return {ret.CANCELLED}
        if obj.type != 'MESH':
            self.report({rep.ERROR_INVALID_INPUT}, 'Mesh type object required')
            return {ret.CANCELLED}
        if obj.parent is None:
            self.report({rep.ERROR_INVALID_INPUT}, 'Active object is not parented')
            return {ret.CANCELLED}

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
            self.report({rep.INFO}, 'Dummies are not found')
            return {ret.FINISHED}

        slot_node = build_tree_with(context.scene.objects, obj.parent)
        root = slot_node.root
        # do not walk into self slot
        slot_node.parent = None
        # tree walking iterator
        nodes_iter = anytree.PreOrderIter(root)
        position_dummies(dummy_verts, nodes_iter)

        if dummy_verts:
            self.report({rep.WARNING}, 'Not all dummies positioned, dumped to the console.')
            print('Not positioned dummies: ', ', '.join(('~' + _id for _id in sorted(dummy_verts))))
        else:
            self.report({rep.INFO}, 'All dummies positioned')

        if me.is_editmode:
            bmesh.update_edit_mesh(me, destructive=False)
        else:
            bm.to_mesh(me)
        me.update()
        return {ret.FINISHED}

    pass


def get_jnodes_co(mesh):
    bm = bmesh.new()
    bm.from_mesh(mesh)
    id_lyr = bm.verts.layers.string['jbeamNodeId']
    for v in bm.verts:
        _id = v[id_lyr].decode()  # decode byte array
        if _id:
            # jnode id is not None and not empty
            yield _id, v.co.copy()


def position_dummies(dummy_verts, tree_nodes):
    """Visit all nodes of the tree and position dummies to their reals.
    After return dummy_verts contains dummies whose reals was not found"""

    # collect all jnode ids and coordinates in the object hierarchy
    jnode_map = {}
    for t_node in tree_nodes:
        if t_node.obj.type == 'MESH':
            # note jnode id can be overwritten during dic.update(), i.e. part's jnode override parent!
            # Is this behavior correct? ToDo check jnode override behavior
            jnode_map.update(get_jnodes_co(t_node.obj.data))

    reals_found = []
    for _id, dummy_v in dummy_verts.items():
        real_co = jnode_map.get(_id, None)
        if real_co:
            dummy_v.co = real_co
            reals_found.append(_id)

    for _id in reals_found:
        dummy_verts.pop(_id)


def build_tree_with(obj_map, specific_obj):
    node_map = {obj.name: Node(obj.name, obj=obj) for obj in obj_map}
    for name, node in node_map.items():
        if node.obj.parent is not None:
            parent_node = node_map.get(node.obj.parent.name, None)
            if parent_node is not None:
                # is parent linked to the scene?
                node.parent = parent_node

    roots = (node for node in node_map.values() if node.parent is None)

    text = bpy.data.texts.get('tree') or bpy.data.texts.new('tree')
    text.clear()
    for rot in roots:
        text.write(str(anytree.RenderTree(rot)) + '\n')

    spec_node = node_map[specific_obj.name]
    return spec_node


class Node(anytree.Node):
    """Tree node, simple repr()"""

    def __repr__(self):
        return self.name
