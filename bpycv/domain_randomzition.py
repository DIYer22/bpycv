#!/usr/bin/env python3

import boxx
from boxx import *

import bpy
import random

from .object_utils import activate_obj, load_obj


def texture_bsdf_dr(obj, shade_smooth_rate=0.9):
    """
    texture domain randomztion for object who has texture, like YCB's model.

    Parameters
    ----------
    obj : object
        object.
    shade_smooth_rate : float, optional
        shade_smooth_rate. The default is 0.9.

    Returns
    -------
    bsdf : Blender's node
        Principled BSDF.

    """
    if random.random() < shade_smooth_rate:
        with activate_obj(obj):
            bpy.ops.object.shade_smooth()

    material = obj.material_slots[0].material
    bsdf = material.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Metallic"].default_value = random.random()
    bsdf.inputs["Specular"].default_value = random.random()
    bsdf.inputs["Specular Tint"].default_value = random.random()
    bsdf.inputs["Roughness"].default_value = random.uniform(0.3, 1)
    bsdf.inputs["Anisotropic"].default_value = random.random()
    bsdf.inputs["Anisotropic Rotation"].default_value = random.random()
    bsdf.inputs["Sheen"].default_value = random.random()
    bsdf.inputs["Sheen Tint"].default_value = random.random()
    bsdf.inputs["Clearcoat"].default_value = random.random()
    bsdf.inputs["Clearcoat Roughness"].default_value = random.random()
    bsdf.inputs["Alpha"].default_value = random.uniform(0.9, 1)
    return bsdf


def load_distractor(distractor_path, target_size="fit_to_YCB"):
    """
    load_distractor, usually using shape net
    
    Notice: shape net's distractor should format by meshlabserver, than import to Blender

    Parameters
    ----------
    distractor_path : str
        distractor path.
    target_size : float, optional
        max side length's lenght. The default is "fit_to_YCB".
        will fit to YCB dataset's size

    Returns
    -------
    distractor.

    """
    if target_size == "fit_to_YCB":
        target_size = random.choice(
            [0.06, 0.1, 0.14, 0.17, 0.18, 0.2, 0.21, 0.23, 0.26, 0.3, 0.35]
        ) * random.uniform(0.8, 1.2)
    distractor = load_obj(distractor_path)
    with activate_obj(distractor):
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")
    distractor.location = (0, 0, 0)
    xyh = [i - j for i, j in zip(distractor.bound_box[-2], distractor.bound_box[0])]
    max_distance = max(map(abs, xyh))
    scale = target_size / max_distance
    distractor.scale = (scale,) * 3
    return distractor


if __name__ == "__main__":
    pass
