#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sun Jan  5 21:41:51 2020
"""

from boxx import *
from boxx import defaultdict


import bpy
import mathutils
import numpy as np

from .physic_utils import OLD_V0_KEY
from .camera_utils import get_cam_intrinsic


T_bcam2cv = np.array(((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)))

# Returns camera rotation and translation matrices from Blender.
#
# There are 3 coordinate systems involved:
#    1. The World coordinates: "world"
#       - right-handed
#    2. The Blender camera coordinates: "bcam"
#       - x is horizontal
#       - y is up
#       - right-handed: negative z look-at direction
#    3. The desired computer vision camera coordinates: "cv"
#       - x is horizontal
#       - y is down (to align to the actual pixel coordinates
#         used in digital images)
#       - right-handed: positive z look-at direction
def get_4x4_world_to_cam_from_blender(camera):
    # bcam stands for blender camera
    R_bcam2cv = mathutils.Matrix(((1, 0, 0), (0, -1, 0), (0, 0, -1)))

    # Use matrix_world instead to account for all constraints
    location, rotation = camera.matrix_world.decompose()[0:2]
    R_world2bcam = rotation.to_matrix().transposed()

    # Convert camera location to translation vector used in coordinate changes
    # Use location from matrix_world to account for constraints:
    T_world2bcam = -1 * R_world2bcam @ location

    # Build the coordinate transform matrix from world to computer vision camera
    R_world2cv = R_bcam2cv @ R_world2bcam
    T_world2cv = R_bcam2cv @ T_world2bcam

    # put into 4x4 matrix
    world_to_cam = mathutils.Matrix(
        (
            R_world2cv[0][:] + (T_world2cv[0],),
            R_world2cv[1][:] + (T_world2cv[1],),
            R_world2cv[2][:] + (T_world2cv[2],),
            (0, 0, 0, 1),
        )
    )
    return world_to_cam


def get_K_world_to_cam(camera):
    K = get_cam_intrinsic(camera)
    world_to_cam = get_4x4_world_to_cam_from_blender(camera)
    return {
        "intrinsic_matrix": np.asarray(K, dtype=np.float32),
        "world_to_cam": np.asarray(world_to_cam, dtype=np.float32),
    }


def matrix_world_for_old_origin(obj):
    matrix_world = obj.matrix_world.copy()
    old_v0 = obj[OLD_V0_KEY]
    to_default_origin_vector = obj.data.vertices[0].co - mathutils.Vector(old_v0)
    matrix_world.translation = (
        matrix_world.translation + matrix_world.to_3x3() @ to_default_origin_vector
    )
    return matrix_world


def homo_coord(points_or_Rt):
    """
    homogeneous coordinates
    """
    if points_or_Rt.shape == (3, 4):
        return np.append(points_or_Rt, [[0, 0, 0, 1]], 0)
    elif points_or_Rt.shape[-1] in {2, 3}:
        return np.append(points_or_Rt, [[1]] * len(points_or_Rt), 1)
    return points_or_Rt


def set_matrix_world(obj, matrix_world):
    """
    Seems only set pose by obj.location and obj.rotation_euler 
    """
    if len(matrix_world) == 3:
        matrix_world = homo_coord(matrix_world)
    obj.location, quaternion, obj.scale = mathutils.Matrix(matrix_world).decompose()
    obj.rotation_euler = quaternion.to_euler()
    return obj


def get_pose_in_cam(obj, cam):
    pose_RT = (
        T_bcam2cv
        @ np.linalg.inv(np.array(cam.matrix_world))
        @ np.array(obj.matrix_world)
    )
    return pose_RT[:3]


def set_pose_in_cam(obj, pose_Rt, cam):
    if len(pose_Rt) == 3:
        pose_Rt = homo_coord(pose_Rt)
    matrix_world = npa(cam.matrix_world) @ T_bcam2cv.T @ pose_Rt
    set_matrix_world(obj, matrix_world)


def get_6d_pose(objs, inst=None, camera=None):
    def inst_id_to_area(inst_id):
        if inst is None:
            return -1
        return (inst == inst_id).sum()

    bpy.context.view_layer.update()
    if camera is None:
        camera = bpy.context.scene.camera
    meta = dict()
    meta.update(get_K_world_to_cam(camera))
    meta["cam_matrix_world"] = np.array(camera.matrix_world)
    for key in [
        "inst_ids",
        "areas",
        "visibles",
        "poses",
        "6ds",
        "bound_boxs",
        "mesh_names",
    ]:
        # default is []
        meta[key] = []
    for obj in objs:
        inst_id = obj.get("inst_id", -1)
        assert inst_id <= 100e4, f"inst_id '{inst_id}' should <= 100e4"
        area = inst_id_to_area(inst_id)
        if area != 0:
            meta["inst_ids"].append(inst_id)
            meta["areas"].append(area)
            meta["visibles"].append(area != 0)

            matrix_world = obj.matrix_world.copy()
            if OLD_V0_KEY in obj:
                matrix_world = matrix_world_for_old_origin(obj)

            pose = np.dot(meta["world_to_cam"], matrix_world)[:3]
            meta["poses"].append(pose[..., None])
            meta["6ds"].append(pose)
            bound_box = np.array([list(point) for point in obj.bound_box])
            meta["bound_boxs"].append(bound_box)
            meta["mesh_names"].append(obj.name)

    meta["poses"] = meta["poses"] and np.concatenate(meta["poses"], -1)
    return dict(meta)


if __name__ == "__main__":
    pass
