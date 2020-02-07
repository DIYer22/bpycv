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
        for obj_idx, obj in enumerate(bpy.data.objects):
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


def load_hdri_world(hdri_path):
    world = bpy.data.worlds[0]
    world.use_nodes = True
    world.node_tree.nodes.clear()
    with activate_node_tree(world.node_tree):
        env_node = Node("ShaderNodeTexEnvironment")
        bg_node = Node("ShaderNodeBackground")
        output_node = Node("ShaderNodeOutputWorld")
        env_node.image = bpy.data.images.load(hdri_path)
        bg_node.Color = env_node.Color
        output_node.Surface = bg_node.Background
    return env_node


if __name__ == "__main__":
    pass
