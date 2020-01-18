#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Thu Jan 16 18:17:20 2020
"""

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


if __name__ == "__main__":
    pass
