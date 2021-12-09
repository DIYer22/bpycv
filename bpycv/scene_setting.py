#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Thu Jan 16 18:17:20 2020
"""
import bpy
import boxx
import random


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


def add_img_background(img_path, size=0.8, domain_random=True):
    """
    Add img as background for domain randomzation, return a PASSIVE rigidbody Plane
    TODO: keep aspect ratio 
    """
    import bpycv

    bpy.ops.mesh.primitive_plane_add(size=size)
    plane = bpy.context.active_object

    with bpycv.activate_obj(plane):
        bpy.ops.rigidbody.object_add()
        plane.rigid_body.type = "PASSIVE"
        bpycv.subdivide(plane, 2048)

        material = bpy.data.materials.new("auto.background.DR")
        material["is_auto"] = True
        material.use_nodes = True
        material.node_tree.nodes.clear()

        with bpycv.activate_node_tree(material.node_tree):
            image_node = bpycv.Node(
                "ShaderNodeTexImage", image=bpy.data.images.load(img_path)
            )
            bsdf_node = bpycv.Node("ShaderNodeBsdfDiffuse")
            bsdf_node.Color = image_node.Color
            bpycv.Node("ShaderNodeOutputMaterial").Surface = bsdf_node.BSDF
            if domain_random:
                image_node.interpolation = random.choice(
                    ["Closest", "Linear", "Cubic", "Smart"]
                )
                bsdf_node.Roughness = random.random()
            else:
                image_node.interpolation = "Linear"
                bsdf_node.Roughness = 1.0
            plane.data.materials.append(material)
    return plane


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


def add_environment_box(xyz=(2, 2, 2), thickness=0.2, transparency=False):
    import bpycv

    xyz = boxx.Vector(xyz)
    thickness += 1
    box = add_stage(size=1, transparency=transparency)
    box.rigid_body.collision_shape = "MESH"
    box.scale = xyz * thickness
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, xyz.z / 2))
    cube = bpy.context.object
    box.location.z = cube.location.z - xyz.z * (thickness - 0.99)
    cube.scale = xyz
    with bpycv.activate_obj(box):
        bpy.ops.object.modifier_add(type="BOOLEAN")
        modifier = box.modifiers[-1]
        modifier.object = cube
        modifier.operation = "DIFFERENCE"
        if bpy.app.version >= (2, 91, 0):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        else:
            bpy.ops.object.modifier_apply(apply_as="DATA", modifier=modifier.name)
    bpycv.remove_obj(cube)
    return box


if __name__ == "__main__":
    pass
