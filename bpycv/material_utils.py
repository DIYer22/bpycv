#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 21:38:05 2019
"""

from boxx import *

import bpy

from .statu_recover import StatuRecover
from .utils import encode_inst_id
from .node_graph import activate_node_tree, Node


class set_inst_material(StatuRecover):
    def __init__(self):
        StatuRecover.__init__(self)

        self.set_attr(bpy.data.worlds[0], "use_nodes", False)
        objs = [obj for obj in bpy.data.objects if obj.type == "MESH"]
        for obj_idx, obj in enumerate(objs):
            if "inst_id" in obj:
                inst_id = obj["inst_id"]
            else:
                inst_id = -1  # -1 as default inst_id
            color = tuple(encode_inst_id.id_to_rgb(inst_id)) + (1,)

            material_name = "auto.inst_material." + obj.name
            material = bpy.data.materials.new(material_name)
            material["is_auto"] = True
            material.use_nodes = True
            material.node_tree.nodes.clear()
            with activate_node_tree(material.node_tree):
                Node("ShaderNodeOutputMaterial").Surface = Node(
                    "ShaderNodeEmission", Color=color
                ).Emission

            self.replace_collection(obj.data.materials, [material])


def remove_mat(mat_or_str):
    if isinstance(mat_or_str, str):
        mat = bpy.data.objects[mat_or_str]
    else:
        mat = mat_or_str
    bpy.data.materials.remove(mat)


if __name__ == "__main__":
    pass
