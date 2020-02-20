#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Thu Jan  2 20:27:57 2020
"""

from boxx import *
from boxx import tree

import bpy
import time
import inspect
from functools import wraps


class StatuRecover:
    def __init__(self):
        self.obj_to_old_attr_value = []
        self.obj_to_old_bpy_prop_collection = {}

    def __enter__(self):
        return self

    def __exit__(self, typee, value, traceback):
        self.recover_statu()

    def recover_statu(self):
        for (obj, attr), value in self.obj_to_old_attr_value[
            ::-1
        ]:  # try avoid TypeError
            try:
                setattr(obj, attr, value)
            except TypeError as e:
                tree - (obj, attr, value)
                print(
                    "Maybe, This value is invalide for other attr, try change order of self.set_attr() in the code"
                )
                # raise e
        for (
            bpy_path,
            bpy_prop_collection,
        ) in self.obj_to_old_bpy_prop_collection.items():
            bpy_path.clear()
            list(map(bpy_path.append, bpy_prop_collection))

    def set_attrs(self, obj, attrs):
        for attr, value in attrs.items():
            self.set_attr(obj, attr, value)

    def set_attr(self, obj, attr, value):
        self.obj_to_old_attr_value.append([(obj, attr), getattr(obj, attr)])
        setattr(obj, attr, value)

    def replace_collection(self, bpy_path, bpy_prop_collection):
        self.obj_to_old_bpy_prop_collection[bpy_path] = bpy_path[:]
        bpy_path.clear()
        list(map(bpy_path.append, bpy_prop_collection))


class undo:
    """ Reverts all changes done to the blender project inside this block.
    Usage: 
        >>> with undo():
                # code
    Reference:
        https://github.com/DLR-RM/BlenderProc/blob/60e559065a4b09db2bd2425822c0ebde9c77609c/src/utility/Utility.py#L200
        
    Warning: undo() may invalid var who point to bpy object, which may cause lots problems.
    """

    def __init__(self, check_point_name=None):
        self.check_point_name = check_point_name

    def __enter__(self):
        check_point_name = self.check_point_name
        if check_point_name is None:
            check_point_name = (
                inspect.stack()[1].filename + " - " + inspect.stack()[1].function
            )
        self.check_point_name = check_point_name
        bpy.ops.ed.undo_push(message="before " + self.check_point_name)

    def __exit__(self, type, value, traceback):
        bpy.ops.ed.undo_push(message="after " + self.check_point_name)
        # The current state points to "after", now by calling undo we go back to "before"
        bpy.ops.ed.undo()

    def __call__(self, func):
        @wraps(func)
        def return_func(*l, **kv):
            with undo(str(time.time())):
                result = func(*l, **kv)
                return result

        return return_func


if __name__ == "__main__":
    pass
