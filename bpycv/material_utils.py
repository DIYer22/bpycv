#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 21:38:05 2019
"""

import boxx
from boxx import *
from boxx import listdir, pathjoin

import bpy
import random

from .utils import encode_inst_id
from .statu_recover import StatuRecover
from .node_graph import activate_node_tree, Node


class set_inst_material(StatuRecover):
    def __init__(self):
        StatuRecover.__init__(self)

        self.set_attr(bpy.data.worlds[0], "use_nodes", False)
        objs = [obj for obj in bpy.data.objects if obj.type in ("MESH", "CURVE")]
        for obj_idx, obj in enumerate(objs):
            inst_id = obj.get("inst_id", 0)  # default inst_id is 0
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


def load_hdri_world(hdri_path, random_rotate_z=False):
    """
    

    Parameters
    ----------
    hdri_path : str
        pass.
    random_rotate_z : bool, optional
        How deg of hdri rotation. The default is False.

    Returns
    -------
    env_node
    """
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
        if random_rotate_z:
            rotate_deg = random.random() * 720
            coord = Node("ShaderNodeTexCoord")
            mapping = Node("ShaderNodeMapping", vector_type="TEXTURE")
            mapping.Vector = coord.Object
            coord.location = -900, 0
            mapping.location = -600, 0
            env_node.Vector = mapping.Vector
            mapping.node.inputs["Rotation"].default_value.z = rotate_deg
    return env_node


def alias_texture_name_to_name(texture_name):
    texture_name = texture_name.lower()
    return texture_name


def get_texture_paths(texture_dir):
    bnames = listdir(texture_dir)
    for i, cs in enumerate(zip(*bnames)):
        if len(set(cs)) != 1:
            break
    for _i, cs in enumerate(zip(*[b[::-1] for b in bnames])):
        if len(set(cs)) != 1:
            break
    texture_paths = {
        alias_texture_name_to_name(bname[i:-_i]): pathjoin(texture_dir, bname)
        for bname in bnames
    }
    texture_paths["name"] = bnames[0][:i] + "." + bnames[0][-_i:]
    return texture_paths


def build_tex(texture_dir):
    texture_paths = get_texture_paths(texture_dir)
    material_name = texture_paths.get("name", "load_mat")
    material = bpy.data.materials.new(material_name)
    material.use_nodes = True
    material.node_tree.nodes.clear()
    material.cycles.displacement_method = "BOTH"
    with activate_node_tree(material.node_tree):
        bsdf = Node("ShaderNodeBsdfPrincipled")
        output = Node("ShaderNodeOutputMaterial")
        output.Surface = bsdf.BSDF
        bsdf.location = 600, 300
        output.location = 900, -200

        coord = Node("ShaderNodeTexCoord")
        mapping = Node("ShaderNodeMapping", vector_type="TEXTURE")
        mapping.Vector = coord.Object
        coord.location = -900, 0
        mapping.location = -600, 0

        diff = Node(
            "ShaderNodeTexImage",
            projection="BOX",
            image=bpy.data.images.load(texture_paths["diff"]),
        )
        diff.Vector = mapping.Vector
        if texture_paths.get("ao"):
            ao_img = bpy.data.images.load(texture_paths["ao"])
            ao_img.colorspace_settings.name = "Non-Color"
            ao = Node("ShaderNodeTexImage", projection="BOX", image=ao_img)

            ao.Vector = mapping.Vector
            mix = Node("ShaderNodeMixRGB", Fac=0.1)
            mix.Color1 = diff.Color
            mix.Color2 = ao.Color
            color_output = mix.Color
        else:
            color_output = diff.Color
        bsdf["Base Color"] = color_output

        rough_img = bpy.data.images.load(texture_paths["rough"])
        rough_img.colorspace_settings.name = "Non-Color"
        rough = Node("ShaderNodeTexImage", projection="BOX", image=rough_img)
        rough.Vector = mapping.Vector
        if texture_paths.get("rough_ao"):
            rough_ao_img = bpy.data.images.load(texture_paths["rough_ao"])
            rough_ao_img.colorspace_settings.name = "Non-Color"
            rough_ao = Node("ShaderNodeTexImage", projection="BOX", image=rough_ao_img)

            rough_ao.Vector = mapping.Vector
            rough_mix = Node("ShaderNodeMixRGB", Fac=0.5)
            rough_mix.Color1 = rough.Color
            rough_mix.Color2 = rough_ao.Color
            rough_output = rough_mix.Color
        else:
            rough_output = rough.Color

        bsdf["Roughness"] = rough_output

        nor_img = bpy.data.images.load(texture_paths["nor"])
        nor_img.colorspace_settings.name = "Non-Color"
        nor = Node("ShaderNodeTexImage", projection="BOX", image=nor_img)
        nor.Vector = mapping.Vector
        normal_map = Node("ShaderNodeNormalMap")
        normal_map.Color = nor.Color
        bsdf.Normal = normal_map.Normal

        disp_img = bpy.data.images.load(texture_paths["disp"])
        disp_img.colorspace_settings.name = "Non-Color"
        disp = Node("ShaderNodeTexImage", projection="BOX", image=disp_img)
        disp.Vector = mapping.Vector
        displacement = Node("ShaderNodeDisplacement", Midlevel=0, Scale=0)
        displacement.Height = disp.Color
        output.Displacement = displacement.Displacement
        mapping.node.inputs["Scale"].default_value = (1.0,) * 3
        mapping.node.inputs["Location"].default_value = [
            random.random() * 8 for _ in "xyz"
        ]

    return material


if __name__ == "__main__":
    pass
