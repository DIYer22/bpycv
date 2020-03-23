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
from mathutils import Matrix
import numpy as np


# we could also define the camera matrix
# https://blender.stackexchange.com/questions/38009/3x4-camera-matrix-from-blender-camera
def get_calibration_matrix_K_from_blender(camera):
    f_in_mm = camera.lens
    scene = bpy.context.scene
    resolution_x_in_px = scene.render.resolution_x
    resolution_y_in_px = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100
    sensor_width_in_mm = camera.sensor_width
    sensor_height_in_mm = camera.sensor_height
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

    if camera.sensor_fit == "VERTICAL":
        # the sensor height is fixed (sensor fit is horizontal),
        # the sensor width is effectively changed with the pixel aspect ratio
        s_u = resolution_x_in_px * scale / sensor_width_in_mm / pixel_aspect_ratio
        s_v = resolution_y_in_px * scale / sensor_height_in_mm
    else:  # 'HORIZONTAL' and 'AUTO'
        # the sensor width is fixed (sensor fit is horizontal),
        # the sensor height is effectively changed with the pixel aspect ratio
        s_u = resolution_x_in_px * scale / sensor_width_in_mm
        s_v = resolution_y_in_px * scale * pixel_aspect_ratio / sensor_height_in_mm

    # Parameters of intrinsic calibration matrix K
    alpha_u = f_in_mm * s_u
    alpha_v = f_in_mm * s_u
    u_0 = resolution_x_in_px * scale / 2
    v_0 = resolution_y_in_px * scale / 2
    skew = 0  # only use rectangular pixels

    K = Matrix(((alpha_u, skew, u_0), (0, alpha_v, v_0), (0, 0, 1)))

    return K


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
def get_3x4_RT_matrix_from_blender(camera):
    # bcam stands for blender camera
    R_bcam2cv = Matrix(((1, 0, 0), (0, -1, 0), (0, 0, -1)))

    # Use matrix_world instead to account for all constraints
    location, rotation = camera.matrix_world.decompose()[0:2]
    R_world2bcam = rotation.to_matrix().transposed()

    # Convert camera location to translation vector used in coordinate changes
    # Use location from matrix_world to account for constraints:
    T_world2bcam = -1 * R_world2bcam @ location

    # Build the coordinate transform matrix from world to computer vision camera
    R_world2cv = R_bcam2cv @ R_world2bcam
    T_world2cv = R_bcam2cv @ T_world2bcam

    # put into 3x4 matrix
    RT = Matrix(
        (
            R_world2cv[0][:] + (T_world2cv[0],),
            R_world2cv[1][:] + (T_world2cv[1],),
            R_world2cv[2][:] + (T_world2cv[2],),
        )
    )
    return RT


def get_3x4_P_matrix_from_blender(camera):
    K = get_calibration_matrix_K_from_blender(camera.data)
    RT = get_3x4_RT_matrix_from_blender(camera)
    return K * RT


def get_K_P_from_blender(camera):
    K = get_calibration_matrix_K_from_blender(camera.data)
    RT = get_3x4_RT_matrix_from_blender(camera)
    RT = np.asarray(RT, dtype=np.float32)
    world_to_cam = np.append(RT, [[0, 0, 0, 1]], axis=0)
    return {
        "intrinsic_matrix": np.asarray(K, dtype=np.float32),
        "world_to_cam": world_to_cam,
    }


def get_6d_pose(objs, inst=None, camera=None):
    def inst_id_to_area(inst_id):
        if inst is None:
            return -1
        return (inst == inst_id).sum()

    bpy.context.view_layer.update()
    if camera is None:
        camera = bpy.context.scene.camera
    meta = defaultdict(lambda: [])
    meta.update(get_K_P_from_blender(camera))
    meta["cam_matrix_world"] = camera.matrix_world
    for obj in objs:
        inst_id = obj.get("inst_id", -1)
        area = inst_id_to_area(inst_id)
        if area != 0:
            meta["inst_ids"].append(inst_id)
            meta["areas"].append(area)
            meta["visibles"].append(area != 0)

            pose = np.dot(meta["world_to_cam"], obj.matrix_world)[:3]
            meta["poses"].append(pose[..., None])
            meta["6ds"].append(pose)
            bound_box = np.array([list(point) for point in obj.bound_box])
            meta["bound_boxs"].append(bound_box)
            meta["mesh_names"].append(obj.name)

    meta["poses"] = meta["poses"] and np.concatenate(meta["poses"], -1)
    return dict(meta)


if __name__ == "__main__":
    pass
