#!/usr/bin/env python3

import bpy
import mathutils

from .object_utils import activate_obj

SET_ORIGIN_HOOK_NAME = "set_back_origin"
OLD_V0_KEY = "old_object.data.vertices[0].co"


def set_origin_and_record_old_v0(obj, type="ORIGIN_CENTER_OF_VOLUME", center="MEDIAN"):
    obj[OLD_V0_KEY] = obj.data.vertices[0].co.copy()
    with activate_obj(obj):
        bpy.ops.object.origin_set(type=type, center=center)


def set_origin_by_vector(obj, new_origin_vector):
    return set_origin_by_point(
        obj, obj.matrix_world.to_translation() + new_origin_vector
    )


def set_origin_by_point(obj, point):
    """
    Not work when bpy.context.scene.frame_curren != 1
    """
    cursor_mat = bpy.context.scene.cursor.matrix.copy()
    bpy.context.scene.cursor.rotation_euler = 0, 0, 0
    bpy.context.scene.cursor.location = point
    with activate_obj(obj):
        bpy.ops.object.origin_set(type="ORIGIN_CURSOR", center="MEDIAN")
    bpy.context.scene.cursor.matrix = cursor_mat
    return obj


if __name__ == "__main__":
    pass
