#!/usr/bin/env python3

from boxx import *
from boxx import deg2rad, np, pi

import bpy
import random


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


if __name__ == "__main__":
    pass
