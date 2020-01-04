#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 21:33:28 2019
"""

from boxx import *
from boxx import inpkg, os, pathjoin, withattr, imread, timeit

import tempfile
import time
import bpy

with inpkg():
    from .select_utils import scene, render
    from .statu_manager import StatuManager

    from .exr_image_parser import parser_exr, ImageWithAnnotation
    from .material_utils import set_inst_map_material


class set_inst_map_render(StatuManager):
    def __init__(self):
        StatuManager.__init__(self)
        self.set_attr(render, "engine", "BLENDER_EEVEE")
        self.set_attr(scene.eevee, "taa_render_samples", 1)
        self.set_attr(scene.eevee, "use_bloom", False)
        attrs = dict(
            file_format="OPEN_EXR",
            color_mode="RGBA",
            color_depth="32",
            use_zbuffer=True,
        )
        self.set_attrs(render.image_settings, attrs)


class set_cycle_render(StatuManager):
    def __init__(self, eevee=False):
        StatuManager.__init__(self)
        self.set_attr(render, "engine", "BLENDER_EEVEE" if eevee else "CYCLES")
        self.set_attr(scene.cycles, "samples", 128)
        self.set_attr(render, "engine", "BLENDER_EEVEE")
        attrs = dict(file_format="PNG", compression=15)
        self.set_attrs(render.image_settings, attrs)
        # render.image_settings.file_format = 'JPEG'
        # render.image_settings.quality = 100


def render_data(render_image=True, render_annotation=True, eevee=False):
    path = pathjoin(tempfile.gettempdir(), "render_" + str(time.time()))
    render_result = {}
    if render_image:
        png_path = path + ".png"
        with set_cycle_render(eevee=eevee), withattr(render, "filepath", png_path):
            bpy.ops.render.render(write_still=True)
        render_result["image"] = imread(png_path)
        os.remove(png_path)

    if render_annotation:
        exr_path = path + ".exr"
        with set_inst_map_material(), set_inst_map_render(), withattr(
            render, "filepath", exr_path
        ):
            bpy.ops.render.render(write_still=True)
        render_result["exr"] = parser_exr(exr_path)
        os.remove(exr_path)
    result = ImageWithAnnotation(**render_result)
    return result


if __name__ == "__main__":
    pass
