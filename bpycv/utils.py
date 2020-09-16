#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Sat Dec 28 20:39:59 2019
"""
import boxx
from boxx import np


class encode_inst_id:
    """
    Encode inst id represent as [0.~1.] float32 rgb, that blender can read as color to render output
    """

    max_depth = 20
    max_denominator = 2 ** max_depth

    @classmethod
    def id_to_rgb(cls, id):
        """
        Cover float[-2**20~2**20] to float32[0.~1.] rgb

        Parameters
        ----------
        id : int, float or numpy
            float[-2**20~2**20].

        Returns
        -------
        (3,)float32
            RGB for Blender.

        """
        if isinstance(id, (float, int)):
            id = np.array(id)
        rgb = np.zeros(id.shape + (3,), dtype=np.float64)
        rgb[..., 0] = id < 0

        absf = np.abs(id)
        int_part = absf // 1
        # rgb[..., 1] = 1 - 1 / (int_part + 1)
        poww = np.int32(np.log2(int_part + 1, dtype=np.float32)) + 1
        denominator = (2 ** poww).round()
        rgb[..., 1] = ((int_part - denominator // 2 + 1) * 2 + 1) / denominator

        rgb[..., 2] = absf % 1
        return rgb

    @classmethod
    def rgb_to_id(cls, rgb):
        is_negative = (-1) ** (rgb[..., 0] == 1)
        # int_part = (1 / (1 - rgb[..., 1]) - 1).round()

        bg_mask = rgb[..., 1] == 0
        rgb[bg_mask, 1] = 0.5

        numerator = (cls.max_denominator * rgb[..., 1]).round().astype(np.int32)
        low_bit = (numerator ^ (numerator - 1)) & numerator
        numerator_odd = numerator // low_bit
        idx_in_level = (numerator_odd - 1) / 2
        up = np.int32(np.log2(low_bit, dtype=np.float32))
        depth = cls.max_depth - up
        int_part = 2 ** (depth - 1) - 1 + idx_in_level
        int_part = np.int32(int_part)

        int_part = int_part * (~bg_mask)
        if rgb[..., 2].any():  # has float
            return is_negative * (int_part + rgb[..., 2])
        else:  # pure int
            return np.int32(is_negative * int_part)

    @classmethod
    def test(cls):
        inst0 = np.arange(-100, 10000)
        inst1 = np.random.randint(
            -cls.max_denominator / 2, cls.max_denominator / 2, (10000)
        )
        inst2 = np.float32(
            np.linspace(-cls.max_denominator / 2, cls.max_denominator / 2, 10000)
        )
        inst3 = np.float32(np.random.rand(10000) * 10000.3 - 1000)
        for inst in [inst0, inst1, inst2, inst3]:
            boxx.tree - inst
            for inst_id in inst.flatten():
                rgb = encode_inst_id.id_to_rgb(inst_id).astype(np.float32)
                # print(rgb, inst_id)
                recover = encode_inst_id.rgb_to_id(rgb)
                boxx.mg()
                assert recover == inst_id, (inst_id, recover)

        assert (
            encode_inst_id.rgb_to_id(np.float32([0, 0, 0])) == 0
        ), "Check background should decode to 0"


def ipython():
    import IPython

    IPython.embed()


if __name__ == "__main__":
    from boxx import *

    encode_inst_id.test()
