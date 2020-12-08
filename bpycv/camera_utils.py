#!/usr/bin/env python3

from boxx import *
from boxx import deg2rad, np, pi

import bpy
import random
import mathutils


def set_cam_pose(cam_radius=1, cam_deg=45, cam_x_deg=None, cam=None):
    cam_rad = deg2rad(cam_deg)
    if cam_x_deg is None:
        cam_x_deg = random.uniform(0, 360)
    cam_x_rad = deg2rad(cam_x_deg)
    z = cam_radius * np.sin(cam_rad)
    xy = (cam_radius ** 2 - z ** 2) ** 0.5
    x = xy * np.cos(cam_x_rad)
    y = xy * np.sin(cam_x_rad)
    cam = cam or bpy.data.objects["Camera"]
    cam.location = x, y, z
    cam.rotation_euler = pi / 2 - cam_rad, 0.1, pi / 2 + cam_x_rad
    cam.scale = (0.1,) * 3
    return cam


def set_cam_intrinsic(cam, intrinsic_K, hw=None):
    """
    K = [[f_x, 0, c_x],
     [0, f_y, c_y],
     [0,   0,   1]]

    Refrence: https://www.rojtberg.net/1601/from-blender-to-opencv-camera-and-back/
    """
    if hw is None:
        scene = bpy.context.scene
        hw = scene.render.resolution_y, scene.render.resolution_x
    near = lambda x, y=0, eps=1e-5: abs(x - y) < eps
    assert near(intrinsic_K[0][1], 0)
    assert near(intrinsic_K[1][0], 0)
    h, w = hw
    f_x = intrinsic_K[0][0]
    f_y = intrinsic_K[1][1]
    c_x = intrinsic_K[0][2]
    c_y = intrinsic_K[1][2]

    cam = cam.data
    cam.shift_x = -(c_x / w - 0.5)
    cam.shift_y = (c_y - 0.5 * h) / w

    cam.lens = f_x / w * cam.sensor_width

    pixel_aspect = f_y / f_x
    scene.render.pixel_aspect_x = 1.0
    scene.render.pixel_aspect_y = pixel_aspect


def get_cam_intrinsic(cam=None):
    """
    we could also define the camera matrix
    https://blender.stackexchange.com/questions/38009/3x4-camera-matrix-from-blender-camera
    """
    cam = cam or bpy.data.objects["Camera"]
    f_in_mm = cam.data.lens
    scene = bpy.context.scene
    resolution_x_in_px = scene.render.resolution_x
    resolution_y_in_px = scene.render.resolution_y
    scale = scene.render.resolution_percentage / 100
    sensor_width_in_mm = cam.data.sensor_width
    sensor_height_in_mm = cam.data.sensor_height
    pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

    if cam.data.sensor_fit == "VERTICAL":
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

    K = mathutils.Matrix(((alpha_u, skew, u_0), (0, alpha_v, v_0), (0, 0, 1)))
    return K


if __name__ == "__main__":
    pass
