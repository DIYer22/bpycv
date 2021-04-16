#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate and visualize 6d pose ground truth in Blender with Python API

Run Command:
    blender --background --python 6d_pose_demo.py
"""

import cv2
import bpy
import bpycv
import boxx
import random
import numpy as np
import scipy.io as sio


def draw_6d_pose(img, xyzs_in_obj, pose, intrinsic, color=(255, 0, 0)):
    R, T = pose[:, :3], pose[:, 3]
    # np.dot(xyzs, R.T) == np.dot(R, xyzs.T).T
    xyzs_in_cam = np.dot(xyzs_in_obj, R.T) + T
    xyzs_in_image = np.dot(xyzs_in_cam, intrinsic.T)
    xys_in_image = xyzs_in_image[:, :2] / xyzs_in_image[:, 2:]
    xys_in_image = xys_in_image.round().astype(int)
    for xy in xys_in_image:
        img = cv2.circle(img, tuple(xy), 10, color, -1)
    return img


def vis_ycb_6d_poses(img, mat, xyzs=None):
    vis = img.copy()
    n = mat["poses"].shape[-1]
    colors = np.array(boxx.getDefaultColorList(n + 3)) * 255  # get some random colors
    for idx in range(n):
        pose = mat["poses"][:, :, idx]
        intrinsic = mat["intrinsic_matrix"]
        if xyzs is None:
            xyzs = mat.get("bound_boxs")[idx]
        draw_6d_pose(vis, xyzs, pose, intrinsic, colors[idx + 1])
    return vis


# remove all MESH objects
[bpy.data.objects.remove(obj) for obj in bpy.data.objects if obj.type == "MESH"]

for inst_id in range(1, 3):
    location = [random.random() * 4 - 2 for _ in range(3)]
    rotation = [random.random() * 2 * np.pi for _ in range(3)]
    # add cube
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    cube = bpy.context.active_object
    # set each instance a unique inst_id, which is used to generate instance annotation.
    cube["inst_id"] = inst_id

result = bpycv.render_data()

# result["ycb_6d_pose"] is 6d pose GT
meta = result["ycb_6d_pose"]
img = result["image"]

# all vertices in cube
cube_xyz = [list(v.co) for v in cube.data.vertices]

vis = vis_ycb_6d_poses(img, meta, cube_xyz)

cv2.imwrite(
    "demo-vis_6d_pose.jpg", cv2.cvtColor(vis, cv2.COLOR_RGB2BGR)
)  # cover RGB to BGR

sio.savemat("ycb_6d_pose.mat", result["ycb_6d_pose"])
print("Saving vis image to:", "./demo-vis_6d_pose.jpg")
