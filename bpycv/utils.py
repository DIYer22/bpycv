#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 20:39:59 2019
"""

from boxx import *
from boxx import np, mg


class encode_inst_id:
    """
    Encode inst id represent as [0.~1.] float64 rgb, that blender can read as color to render output
    """

    @staticmethod
    def id_to_rgb(f):
        if isinstance(f, (float, int)):
            f = np.array(f)
        rgb = np.zeros(f.shape + (3,), dtype=np.float64)
        rgb[..., 0] = f < 0
        absf = np.abs(f)
        int_part = absf // 1
        rgb[..., 1] = 1 - 1 / (int_part + 1)
        rgb[..., 2] = absf % 1
        return rgb

    @staticmethod
    def rgb_to_id(rgb):
        is_negative = (-1) ** (rgb[..., 0] == 1)
        int_part = (1 / (1 - rgb[..., 1]) - 1).round()
        if rgb[..., 2].any():  # has float
            return is_negative * (int_part + rgb[..., 2])
        else:  # pure int
            return np.int32(is_negative * int_part)

    @staticmethod
    def test():
        inst1 = np.random.rand(10, 10) * 100000.3 - 1000
        inst2 = np.random.randint(-100000, 100000, (10, 10))
        for inst in [inst1, inst2]:
            rgb = encode_inst_id.id_to_rgb(inst)
            recover = encode_inst_id.rgb_to_id(rgb)
            mg()
            assert (inst == recover).all()


def ipython():
    import IPython

    IPython.embed()


if __name__ == "__main__":
    encode_inst_id.test()
