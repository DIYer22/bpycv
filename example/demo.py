#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Notice: When update demo.py: 
    1. Update README.md
    2. @diyer22 update the answer on stackexchange:
            https://blender.stackexchange.com/a/162746/86396 
"""

import cv2
import bpy
import bpycv
import random

# remove all MESH objects
[bpy.data.objects.remove(obj) for obj in bpy.data.objects if obj.type == "MESH"]

for inst_id in range(1, 20):
    # create cube and sphere as instance at random location
    location = [random.random() * 4 - 2 for _ in range(3)]
    if inst_id % 2:
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=location)
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=location)
    obj = bpy.context.active_object
    # set each instance a unique inst_id, which is used to generate instance annotation.
    obj["inst_id"] = inst_id

# render image, instance annoatation and depth in one line code
# result["ycb_6d_pose"] is 6d pose GT
result = bpycv.render_data()

# save result
cv2.imwrite(
    "demo-rgb.jpg", cv2.cvtColor(result["image"], cv2.COLOR_RGB2BGR)  # cover RGB to BGR
)
cv2.imwrite("demo-inst.png", result["inst"])
# normalizing depth
cv2.imwrite("demo-depth.png", result["depth"] / result["depth"].max() * 255)

# visualization inst|rgb|depth for human
cv2.imwrite(
    "demo-vis(inst|rgb|depth).jpg", cv2.cvtColor(result.vis(), cv2.COLOR_RGB2BGR)
)
