#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 20:51:37 2019
"""

from boxx import *
from boxx import inpkg, pd

import bpy


def is_obj_valid(obj):
    try:
        dir(obj)
        return True
    except ReferenceError:
        return False


class activate_obj(object):
    def __init__(self, obj):
        self.current_obj = bpy.context.active_object
        bpy.context.view_layer.objects.active = obj

    def __enter__(self):
        return self

    def __exit__(self, typee, value, traceback):
        if is_obj_valid(self.current_obj):
            bpy.context.view_layer.objects.active = self.current_obj


def remove_obj(obj_or_str):
    if isinstance(obj_or_str, str):
        obj = bpy.data.objects[obj_or_str]
    else:
        obj = obj_or_str
    bpy.data.objects.remove(obj)


if __name__ == "__main__":
    pass
