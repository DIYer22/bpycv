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
    from .camera_utils import get_cam_intrinsic

import os
import struct

import bpy
import cv2
import minexr
import scipy.io


def depth_of_point_to_depth(depth_of_point, K):
    """
    # https://blender.stackexchange.com/questions/130970/cycles-generates-distorted-depth
    CYCLES's depth is distance to camera original point
    EEVEE's dpeth is XYZ's Z, same to opencv
    """
    h, w = depth_of_point.shape
    xyzs_1m = (
        np.pad(
            np.mgrid[:h, :w][::-1].reshape(2, -1), ((0, 1), (0, 0)), constant_values=1
        ).T
        @ np.linalg.inv(K).T
    )
    xyzs = (
        xyzs_1m
        * depth_of_point.flatten()[:, None]
        / np.linalg.norm(xyzs_1m, axis=1, keepdims=True)
    )
    depth = xyzs[:, 2].reshape(h, w)
    return depth


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

    def __init__(self, exr_path, K=None):
        with open(exr_path, "rb") as fp:
            self.reader = ExrReader(fp)
        self.by_cycles = any(
            [key for key in self.reader.attrs if key.startswith("cycles.")]
        )
        if self.by_cycles and K is None:  # CYCLES has different depth
            K = get_cam_intrinsic()
        self.K = K

    def get_rgb(self):
        return self.reader.select(["R", "G", "B"]).copy()

    def get_rgba(self):
        return self.reader.select(["R", "G", "B", "A"]).copy()

    def get_raw_depth(self):
        raw_depth = self.reader.select(["Z"]).copy().squeeze()
        if self.by_cycles:
            raw_depth = depth_of_point_to_depth(raw_depth, self.K)
        return raw_depth

    def get_pseudo_color(self):
        depth = self.get_raw_depth()
        limit_mask = depth < self.LIMIT_DEPTH
        depth = depth * limit_mask
        depth = depth / depth.max()
        depth[~limit_mask] = 1.1
        depth = 1 - depth
        return heatmap_to_pseudo_color(depth)

    def get_depth(self):
        # turn inf depth to 0
        depth = self.get_raw_depth()
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
        if image is not None:
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

        image = self.get("image", self.get("image1"))
        if image is not None:
            vis_list.append(image[..., :3] / 255.0)

        depth_vis = self["_raw_exr"].get_pseudo_color()
        vis_list.append(depth_vis)
        vis = (np.concatenate(vis_list, 1) * 255).astype(np.uint8)
        return vis

    def save(
        self, dataset_dir="dataset", fname="0", save_blend=False, no_sub_dir=False
    ):
        fname = str(fname)
        os.makedirs(dataset_dir, exist_ok=True)

        def split_by_datatype_prefix(fname, type_name):
            sub_dir = pathjoin(dataset_dir, type_name)
            os.makedirs(sub_dir, exist_ok=True)
            return sub_dir + "/" + fname

        no_sub_dir_prefix = lambda fname, type_name: pathjoin(
            dataset_dir, f"{fname}~{type_name}"
        )
        get_prefix = no_sub_dir_prefix if no_sub_dir else split_by_datatype_prefix

        if self.get("inst") is not None:
            inst_prefix = get_prefix(fname, "instance_map")
            inst_path = inst_prefix + ".png"
            cv2.imwrite(inst_path, self["inst"].clip(0).astype(np.uint16))
        if self.get("depth") is not None:
            depth_prefix = get_prefix(fname, "depth")
            depth_path = depth_prefix
            if self["depth"].dtype == np.uint16:
                cv2.imwrite(depth_path + ".png", self["depth"])
            else:
                savenp(depth_path, self["depth"].astype(np.float16))
        if (
            self.get("image", self.get("image1")) is not None
            and self.get("inst") is not None
            and self.get("depth") is not None
        ):
            vis_prefix = get_prefix(fname, "vis")
            vis_path = vis_prefix + ".jpg"
            cv2.imwrite(vis_path, self.vis()[..., ::-1])
        if self.get("ycb_6d_pose") is not None:
            pose_prefix = get_prefix(fname, "ycb_6d_pose")
            pose_path = pose_prefix + ".mat"
            scipy.io.savemat(pose_path, self["ycb_6d_pose"])
        if save_blend:
            blend_prefix = get_prefix(fname, "blend")
            blend_path = blend_prefix + ".blend"
            bpy.ops.wm.save_mainfile(filepath=os.path.abspath(blend_path))
        # save image at last for unstable compute enviroment
        def save_rgb_image(key):
            if self.get(key) is not None:
                image_prefix = get_prefix(fname, key)
                image_path = image_prefix + ".jpg"
                cv2.imwrite(image_path, self[key][..., ::-1])

        save_rgb_image("image")
        save_rgb_image("image1")
        save_rgb_image("image2")


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
