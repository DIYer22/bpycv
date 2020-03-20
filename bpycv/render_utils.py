#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 21:33:28 2019
"""

from boxx import *
from boxx import os, pathjoin, withattr, imread, sysi

import bpy
import time
import tempfile

from .select_utils import scene, render
from .statu_recover import StatuRecover, undo
from .exr_image_parser import parser_exr, ImageWithAnnotation
from .material_utils import set_inst_material
from .pose_utils import get_6d_pose


class set_annotation_render(StatuRecover):
    def __init__(self):
        StatuRecover.__init__(self)
        # TODO detect whether in ssh X11 forward
        # if sysi.gui:  # mean "does the enviroment support GUI".
        # self.set_attr(render, "engine", "BLENDER_EEVEE")
        if render.engine == "BLENDER_WORKBENCH":
            self.set_attr(render, "engine", "CYCLES")
        if render.engine == "BLENDER_EEVEE":
            # When enviroment not support GUI, Eevee will raise Exception("Unable to open a display")  (@Blender 2.81)
            self.set_attr(render, "engine", "BLENDER_EEVEE")
            self.set_attr(scene.eevee, "taa_render_samples", 1)
            self.set_attr(scene.eevee, "use_bloom", False)
        elif render.engine == "CYCLES":
            self.set_attr(render, "engine", "CYCLES")
            self.set_attr(scene.cycles, "samples", 1)
            self.set_attr(
                scene.view_layers["View Layer"].cycles, "use_denoising", False
            )
        self.set_attr(render, "film_transparent", True)
        self.set_attr(scene.render, "use_motion_blur", False)
        self.set_attr(scene.render, "tile_x", 256)
        self.set_attr(scene.render, "tile_y", 256)

        attrs = dict(
            file_format="OPEN_EXR",
            color_mode="RGBA",
            color_depth="32",
            use_zbuffer=True,
        )
        self.set_attrs(render.image_settings, attrs)


class set_image_render(StatuRecover):
    def __init__(self):
        StatuRecover.__init__(self)
        # self.set_attr(render, "engine", "BLENDER_EEVEE" if eevee else "CYCLES")
        # self.set_attr(scene.cycles, "samples", 128)
        attrs = dict(file_format="PNG", compression=15)
        self.set_attrs(render.image_settings, attrs)
        # render.image_settings.file_format = 'JPEG'
        # render.image_settings.quality = 100


# @undo()
def render_data(render_image=True, render_annotation=True):
    path = pathjoin(tempfile.gettempdir(), "render_" + str(time.time()))
    render_result = {}
    if render_image:
        png_path = path + ".png"
        with set_image_render(), withattr(render, "filepath", png_path):
            print("Render image using:", render.engine)
            bpy.ops.render.render(write_still=True)
        render_result["image"] = imread(png_path)[..., :3]
        os.remove(png_path)

    if render_annotation:
        exr_path = path + ".exr"
        with set_inst_material(), set_annotation_render(), withattr(
            render, "filepath", exr_path
        ):
            print("Render annotation using:", render.engine)
            bpy.ops.render.render(write_still=True)
        render_result["exr"] = parser_exr(exr_path)
        os.remove(exr_path)
    result = ImageWithAnnotation(**render_result)
    if "render_6d_pose":
        objs = [obj for obj in bpy.data.objects if "inst_id" in obj]
        ycb_6d_pose = get_6d_pose(objs, inst=result["inst"])
        result["ycb_6d_pose"] = ycb_6d_pose
    return result


if __name__ == "__main__":
    pass
