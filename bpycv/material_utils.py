#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 21:38:05 2019
"""

from boxx import *
from boxx import inpkg

import bpy

with inpkg():
    from .statu_manager import StatuManager
    from .utils import encode_inst_id


class set_inst_map_material(StatuManager):
    def __init__(self):
        StatuManager.__init__(self)

        self.set_attr(bpy.data.worlds[0], "use_nodes", False)
        objs = [obj for obj in bpy.data.objects if obj.type == "MESH"]
        for obj_idx, obj in enumerate(objs):
            material_name = "auto.inst_map_material." + obj.name
            material = bpy.data.materials.new(material_name)
            material["is_auto"] = True
            material.use_nodes = True
            material.node_tree.nodes.clear()
            output_node = material.node_tree.nodes.new("ShaderNodeOutputMaterial")
            emission_node = material.node_tree.nodes.new("ShaderNodeEmission")
            material.node_tree.links.new(
                emission_node.outputs["Emission"], output_node.inputs[0]
            )
            if "inst_id" in obj:
                inst_id = obj["inst_id"] + 1
            else:
                inst_id = -1  # -1 as default inst_id
            color = tuple(encode_inst_id.id_to_rgb(inst_id))
            emission_node.inputs[0].default_value = color + (1,)
            self.replace_collection(obj.data.materials, [material])


def remove_mat(mat_or_str):
    if isinstance(mat_or_str, str):
        mat = bpy.data.objects[mat_or_str]
    else:
        mat = mat_or_str
    bpy.data.materials.remove(mat)


if __name__ == "__main__":
    pass
