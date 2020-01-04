#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Fri Jan  3 21:44:02 2020
"""

import cv2
import bpy
import random

from bpycv import render_data

[bpy.data.objects.remove(obj) for obj in bpy.data.objects if obj.type=="MESH"]

for inst_id in range(1, 20):
    location = [random.random()* 4 - 2 for _ in range(3)]
    if inst_id % 2:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=location)
    else:
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=location)
    obj = bpy.context.active_object
    obj[inst_id] = inst_id

result = render_data(eevee=True)
cv2.imsave("demo.png", result["depth"])
cv2.imsave("demo.tif", result["inst"])
cv2.imsave("demo.jpg", result["image"])

    


if __name__ == "__main__":
    pass
    
    
    
