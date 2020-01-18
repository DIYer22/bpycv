#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 20:51:37 2019
"""

from boxx import *

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


class edit_mode:
    def __init__(self, obj=None, mode="EDIT"):
        self.obj = obj
        self.mode = mode

    def __enter__(self):
        if self.obj is None:
            self.obj = bpy.context.object
        self.activate = activate_obj(self.obj)
        self.activate.__enter__()
        self.old_mode = self.obj.mode
        bpy.ops.object.mode_set(mode=self.mode)

    def __exit__(self, typee, value, traceback):
        bpy.ops.object.mode_set(mode=self.old_mode)
        self.activate.__exit__(typee, value, traceback)


def subdivide(obj, number_cuts=2):
    with edit_mode(obj):
        bpy.ops.mesh.subdivide(number_cuts=number_cuts)


def duplicate(obj, copy_data=False, collection=None):
    if collection is None:
        collection = bpy.context.collection
    new_obj = obj.copy()
    if copy_data:
        new_obj.data = obj.data.copy()
    collection.objects.link(new_obj)
    return new_obj


if __name__ == "__main__":
    pass
