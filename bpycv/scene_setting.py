#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Thu Jan 16 18:17:20 2020
"""

from boxx import *

import bpy


def remove_useless_data():
    """
    remove all data and release RAM
    """
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)

    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)

    for block in bpy.data.textures:
        if block.users == 0:
            bpy.data.textures.remove(block)

    for block in bpy.data.images:
        if block.users == 0:
            bpy.data.images.remove(block)


def clear_all():
    [
        bpy.data.objects.remove(obj)
        for obj in bpy.data.objects
        if obj.type in ("MESH", "LIGHT", "CURVE")
    ]
    remove_useless_data()


def set_shading_mode(mode="SOLID", screens=[]):
    """
    Performs an action analogous to clicking on the display/shade button of
    the 3D view. Mode is one of "RENDERED", "MATERIAL", "SOLID", "WIREFRAME".
    The change is applied to the given collection of bpy.data.screens.
    If none is given, the function is applied to bpy.context.screen (the
    active screen) only. E.g. set all screens to rendered mode:
      set_shading_mode("RENDERED", bpy.data.screens)
    """
    screens = screens if screens else [bpy.context.screen]
    for s in screens:
        for spc in s.areas:
            if spc.type == "VIEW_3D":
                spc.spaces[0].shading.type = mode
                break  # we expect at most 1 VIEW_3D space


def add_stage(size=2, transparency=False):
    """
    add PASSIVE rigidbody cube for physic stage or depth background 

    Parameters
    ----------
    size : float, optional
        size of stage. The default is 2.
    transparency : bool, optional
        transparency for rgb but set limit for depth. The default is False.
    """
    import bpycv

    bpy.ops.mesh.primitive_cube_add(size=size, location=(0, 0, -size / 2))
    stage = bpy.context.active_object
    stage.name = "stage"
    with bpycv.activate_obj(stage):
        bpy.ops.rigidbody.object_add()
        stage.rigid_body.type = "PASSIVE"
        if transparency:
            stage.rigid_body.use_margin = True
            stage.rigid_body.collision_margin = 0.04
            stage.location.z -= stage.rigid_body.collision_margin

            material = bpy.data.materials.new("transparency_stage_bpycv")
            material.use_nodes = True
            material.node_tree.nodes.clear()
            with bpycv.activate_node_tree(material.node_tree):
                bpycv.Node("ShaderNodeOutputMaterial").Surface = bpycv.Node(
                    "ShaderNodeBsdfPrincipled", Alpha=0
                ).BSDF
            stage.data.materials.append(material)
    return stage


if __name__ == "__main__":
    pass
