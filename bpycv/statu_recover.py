#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Thu Jan  2 20:27:57 2020
"""

from boxx import *
from boxx import tree


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
                raise e
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


if __name__ == "__main__":
    pass
