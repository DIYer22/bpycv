#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 20:56:00 2019
"""

from boxx import *
from boxx import pd

import bpy

objs = bpy.data.objects
scene = bpy.data.scenes[0]
render = scene.render
cam = bpy.data.objects.get("Camera", None)
world = bpy.data.worlds[0]


def get_objdf():
    row_dics = []

    def obj_to_row(obj):
        return dict(key=obj.name, type=obj.type, obj=obj)

    for k, obj in bpy.data.objects.items():
        row_dic = obj_to_row(obj)
        row_dics.append(row_dic)

    return pd.DataFrame(row_dics)


if __name__ == "__main__":
    pass
