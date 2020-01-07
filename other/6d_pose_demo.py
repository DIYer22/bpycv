#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Mon Jan  6 19:03:28 2020

generate and visualize 6d pose ground truth in Blender with Python API
"""

from boxx import *
from boxx import np, npa, getDefaultColorList, pi

import cv2
import bpy
import bpycv
import random


def vis_pose(img, xyzs, pose, K, color=None):
    xyz2 = np.dot(xyzs, pose[:, :3].T) + pose[:, 3]
    p_p3d = np.dot(xyz2, K.T)
    p_p3d[:, 0] = p_p3d[:, 0] / p_p3d[:, 2]
    p_p3d[:, 1] = p_p3d[:, 1] / p_p3d[:, 2]
    p2ds = p_p3d[:, :2].astype(np.int)
    for p2d in p2ds:
        img = cv2.circle(img, (p2d[0], p2d[1]), 10, color, -1)
    return img


def vis_poses_by_meta(img, meta, xyzs=None):
    n = meta["poses"].shape[-1]
    colors = npa(getDefaultColorList(n + 3)) * 255
    for idx in range(n):
        pose = meta["poses"][:, :, idx]
        K = meta["intrinsic_matrix"]
        if xyzs is None:
            xyzs = meta.get("bound_boxs")[idx]
        img = vis_pose(img, xyzs, pose, K, colors[idx + 1])
    return img


# remove all MESH objects
[bpy.data.objects.remove(obj) for obj in bpy.data.objects if obj.type == "MESH"]

cube_size = 1
for inst_id in range(1, 3):
    location = [random.random() * 4 - 2 for _ in range(3)]
    rotation = [random.random() * 2 * pi for _ in range(3)]
    # add cube
    bpy.ops.mesh.primitive_cube_add(
        size=cube_size, location=location, rotation=rotation
    )
    obj = bpy.context.active_object
    # set each instance a unique inst_id, which is used to generate instance annotation.
    obj["inst_id"] = inst_id

# result["ycb_meta"] is 6d pose GT
result = bpycv.render_data()

meta = result["ycb_meta"]
img = result["image"]

# cube mesh xyz
cube_xyz_s = "111 110 101 011 100 010 001 000"
cube_xyz = np.array(
    [[-cube_size / 2, cube_size / 2][int(s)] for s in cube_xyz_s if s in "01"]
).reshape(-1, 3)
cube_xyz = None
vis = vis_poses_by_meta(img, meta, cube_xyz)

cv2.imwrite("demo-vis_6d_pose.jpg", vis)

if __name__ == "__main__":
    pass
