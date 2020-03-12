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


def _vis_pose(img, xyzs, pose, K, color=None):
    xyz2 = np.dot(xyzs, pose[:, :3].T) + pose[:, 3]
    p_p3d = np.dot(xyz2, K.T)
    p_p3d[:, 0] = p_p3d[:, 0] / p_p3d[:, 2]
    p_p3d[:, 1] = p_p3d[:, 1] / p_p3d[:, 2]
    p2ds = p_p3d[:, :2].astype(np.int)
    for p2d in p2ds:
        img = cv2.circle(img, (p2d[0], p2d[1]), 10, color, -1)
    return img


def vis_poses_by_ycb_6d_pose(img, meta, xyzs=None):
    n = meta["poses"].shape[-1]
    colors = np.array(boxx.getDefaultColorList(n + 3)) * 255  # get some random colors
    for idx in range(n):
        pose = meta["poses"][:, :, idx]
        K = meta["intrinsic_matrix"]
        if xyzs is None:
            xyzs = meta.get("bound_boxs")[idx]
        img = _vis_pose(img, xyzs, pose, K, colors[idx + 1])
    return img


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

vis = vis_poses_by_ycb_6d_pose(img, meta, cube_xyz)

cv2.imwrite(
    "demo-vis_6d_pose.jpg", cv2.cvtColor(vis, cv2.COLOR_RGB2BGR)
)  # cover RGB to BGR

sio.savemat("ycb_6d_pose.mat", result["ycb_6d_pose"])
print("Saving vis image to:", "./demo-vis_6d_pose.jpg")
