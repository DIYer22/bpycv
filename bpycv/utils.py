#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 20:39:59 2019
"""

from boxx import *
from boxx import np


class encode_inst_id:
    """
    Encode inst id represent as [0.~1.] float64 rgb, that blender can read as color to render output
    """

    instn = 20  # How many inst would distinguishable for vis

    @staticmethod
    def id_to_rgb(f):
        if isinstance(f, (float, int)):
            f = np.array(f)
        rgb = np.zeros(f.shape + (3,), dtype=np.float64)
        rgb[..., 0] = f < 0
        absf = np.abs(f)
        rgb[..., 1] = 1 - np.exp(-(absf // 1 / encode_inst_id.instn))
        rgb[..., 2] = absf % 1
        return rgb

    @staticmethod
    def rgb_to_id(rgb):
        is_negative = (-1) ** rgb[..., 0]
        int_part = (-np.log(1 - rgb[..., 1]) * encode_inst_id.instn).round()
        if rgb[..., 2].any():  # has float
            return is_negative * (int_part + rgb[..., 2])
        else:  # pure int
            return np.int32(is_negative * int_part)


if __name__ == "__main__":
    pass
