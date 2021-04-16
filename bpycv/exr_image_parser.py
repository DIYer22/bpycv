#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Thu Dec 26 18:15:47 2019
"""
import boxx
from boxx import *
from boxx import greyToRgb, histEqualize, inpkg, np, pathjoin, savenp

with inpkg():
    from .pseudo_color import heatmap_to_pseudo_color
    from .utils import encode_inst_id

import os
import struct

import bpy
import cv2
import minexr
import scipy.io


class ExrReader(minexr.reader.MinExrReader):
    def _read_image(self):
        """
        Override original _read_image, since that one assumes ims are float16 but we use float32 here
        """
        H, C, W = self.shape

        dtype = self.channel_types[0]
        DS = np.dtype(dtype).itemsize
        SOFF = 8 + DS * W * C
        strides = (SOFF, DS * W, DS)
        nbytes = SOFF * H

        self.fp.seek(self.first_offset, 0)
        image = np.frombuffer(self.fp.read(nbytes), dtype=dtype, count=-1, offset=8)
        self.image = np.lib.stride_tricks.as_strided(image, (H, C, W), strides)

    def _read_header(self):
        """
        Override original _read_header, since that one doesn't allow for cycles' long attribute names
        """
        self.fp.seek(0)
        buf = minexr.buffer.BufferReader(self.fp.read(10000))

        # Magic and version and info bits
        magic, version, b2, b3, b4 = struct.unpack("<iB3B", buf.read(8))
        assert magic == 20000630, "Not an OpenEXR file."
        assert b3 == b4 == 0, "Not a single-part scan line file."
        assert b2 in (0, 4), "Not a single-part scan line file."

        # Header attributes
        self.attrs = self._read_header_attrs(buf)

        # Parse channels and datawindow
        self.compr = self._parse_compression(self.attrs)
        self.channel_names, self.channel_types = self._parse_channels(self.attrs)
        self.channel_map = {cn: i for i, cn in enumerate(self.channel_names)}
        H, W = self._parse_data_window(self.attrs)
        self.shape = (H, len(self.channel_names), W)
        self.first_offset = self._read_first_offset(buf)

        # Assert our assumptions
        assert self.compr == 0x00, "Compression not supported."
        assert len(set(self.channel_types)) <= 1, "All channel types must be equal."


class ExrImage:
    LIMIT_DEPTH = 6e4

    def __init__(self, exr_path):
        with open(exr_path, "rb") as fp:
            self.reader = ExrReader(fp)

    def get_rgb(self):
        return self.reader.select(["R", "G", "B"]).copy()

    def get_rgba(self):
        return self.reader.select(["R", "G", "B", "A"]).copy()

    def get_pseudo_color(self):
        depth = self.reader.select(["Z"]).copy().squeeze()
        limit_mask = depth < self.LIMIT_DEPTH
        depth = depth * limit_mask
        depth = depth / depth.max()
        depth[~limit_mask] = 1.1
        depth = 1 - depth
        return heatmap_to_pseudo_color(depth)

    def get_depth(self):
        # turn inf depth to 0
        depth = self.reader.select(["Z"]).copy().squeeze()
        limit_mask = depth < self.LIMIT_DEPTH
        depth = depth * limit_mask
        return depth

    def get_inst(self):
        rgb = self.get_rgb()
        inst = encode_inst_id.rgb_to_id(rgb)

        # if world.use_nodes is False, Blender will set background as a gray (0.05087609, 0.05087609, 0.05087609)
        gray_background_mask = (rgb[..., 0] != 0) & (rgb[..., 0] != 1)
        inst[gray_background_mask] = -1
        return inst


class ImageWithAnnotation(dict):
    def __init__(self, image=None, exr=None, **kv):
        super().__init__(**kv)
        self["image"] = image
        self["inst"] = exr.get_inst()
        self["depth"] = exr.get_depth()
        self["_raw_exr"] = exr

    def __getattribute__(self, key):
        if key in self:
            return self[key]
        return dict.__getattribute__(self, key)

    def vis(self):
        vis_list = []  # RGB float 0.~1.

        def vis_inst(inst):
            unique, _idxs = np.unique(inst, return_inverse=True)
            idxs = _idxs.reshape(inst.shape)
            return boxx.mapping_array(
                idxs, boxx.getDefaultColorList(len(unique), includeBackGround=True)
            )

        if "inst" in self:
            inst_vis = vis_inst(self["inst"])
            vis_list.append(inst_vis)

        if self.get("image") is not None:
            image = self["image"]
            vis_list.append(image[..., :3] / 255.0)

        depth_vis = self["_raw_exr"].get_pseudo_color()
        vis_list.append(depth_vis)
        vis = (np.concatenate(vis_list, 1) * 255).astype(np.uint8)
        return vis

    def save(self, dataset_dir="dataset", fname="0", save_blend=False):
        fname = str(fname)
        if self.get("inst") is not None:
            inst_dir = pathjoin(dataset_dir, "instance_map")
            os.makedirs(inst_dir, exist_ok=True)
            inst_path = pathjoin(inst_dir, fname + ".png")
            cv2.imwrite(inst_path, self["inst"].clip(0).astype(np.uint16))
        if self.get("depth") is not None:
            depth_dir = pathjoin(dataset_dir, "depth")
            os.makedirs(depth_dir, exist_ok=True)
            depth_path = pathjoin(depth_dir, fname)
            savenp(depth_path, self["depth"].astype(np.float16))
        if (
            self.get("image") is not None
            and self.get("inst") is not None
            and self.get("depth") is not None
        ):
            vis_dir = pathjoin(dataset_dir, "vis")
            os.makedirs(vis_dir, exist_ok=True)
            vis_path = pathjoin(vis_dir, fname + ".jpg")
            cv2.imwrite(vis_path, self.vis()[..., ::-1])
        if self.get("ycb_6d_pose") is not None:
            pose_dir = pathjoin(dataset_dir, "ycb_6d_pose")
            os.makedirs(pose_dir, exist_ok=True)
            pose_path = pathjoin(pose_dir, fname + ".mat")
            scipy.io.savemat(pose_path, self["ycb_6d_pose"])
        if save_blend:
            blend_dir = pathjoin(dataset_dir, "blend")
            os.makedirs(blend_dir, exist_ok=True)
            blend_path = pathjoin(blend_dir, fname + ".blend")
            bpy.ops.wm.save_mainfile(filepath=blend_path)
        # save image at last for unstable compute enviroment
        if self.get("image") is not None:
            image_dir = pathjoin(dataset_dir, "image")
            os.makedirs(image_dir, exist_ok=True)
            image_path = pathjoin(image_dir, fname + ".jpg")
            cv2.imwrite(image_path, self["image"][..., ::-1])


def parser_exr(exr_path):
    exr = ExrImage(exr_path)
    return exr


def test_parser_exr(exr_path="../tmp_exrs/cycles.exr"):
    return parser_exr(exr_path)


if __name__ == "__main__":
    from boxx import imread, show

    exr_path = "../example/tmp_exr/inst.exr"
    exr = parser_exr(exr_path)
    inst = exr.get_inst()
    png = np.uint8(boxx.mapping_array(inst % 20, boxx.getDefaultColorList(20)) * 255)

    ann = ImageWithAnnotation(png, exr)
    vis = ann.vis()
    show - vis
