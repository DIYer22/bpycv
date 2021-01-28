#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Tue Feb 18 18:15:29 2020
"""

import boxx
from boxx import os
from boxx import timeit, pathjoin

import bpy
import time
import random
from abc import abstractmethod

uniform_by_mean = lambda mean, rate=0.2: random.uniform(-1, 1) * mean * rate + mean


class MetaDatasetGenerator:
    def __init__(self, cfg):
        self.cfg = cfg
        self._blender_setting()

    def _blender_setting(self):
        render = bpy.data.scenes[0].render
        render.engine = "CYCLES"
        render.resolution_x = self.cfg.RESOLUTION[1]
        render.resolution_y = self.cfg.RESOLUTION[0]

        bpy.context.scene.frame_end = 168
        bpy.context.scene.frame_set(0)

        if self.cfg.DEBUG:
            bpy.context.scene.view_layers[0].cycles.use_denoising = False
            bpy.context.scene.cycles.samples = 8
        bpy.context.view_layer.update()

    @abstractmethod
    def generate_one(self, dirr, index):
        pass

    def exist(self, dirr, index):
        return os.path.isfile(pathjoin(dirr, "image", f"{index}.jpg"))

    def resample_keys(self, keys):
        try:
            keys = __import__("brainpp_yl").split_keys_by_replica(keys[:])
        except ModuleNotFoundError:
            pass
        return keys

    def generate_all(self):
        abs_dir = os.path.abspath(self.cfg.DIR)
        keys = range(self.cfg.IMG_NUM)

        if self.cfg.DEBUG:
            self.generate_one(abs_dir, str(int(time.time())))
            boxx.pred(abs_dir)
            return
        keys = self.resample_keys(keys)
        for index in keys:
            if not self.exist(abs_dir, index):
                with timeit("generate_one"):
                    self.generate_one(abs_dir, index)


if __name__ == "__main__":
    pass
