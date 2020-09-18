#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: DIYer22@github
@mail: ylxx@live.com
Created on Thu Dec 26 18:15:47 2019
"""
from boxx import *
from boxx import np, inpkg, greyToRgb, histEqualize, pathjoin, savenp

with inpkg():
    from .pseudo_color import heatmap_to_pseudo_color
    from .utils import encode_inst_id

import os
import cv2
import OpenEXR
import scipy.io


class ExrDict(dict):
    LIMIT_DEPTH = 6e4

    def __getattribute__(self, key):
        if key in self:
            return self[key]
        return dict.__getattribute__(self, key)

    def get_rgb(self):
        return np.concatenate(
            [self["R"][..., None], self["G"][..., None], self["B"][..., None]], -1
        )

    def get_rgba(self):
        return np.concatenate([self.get_rgb(), self["A"][..., None]], -1)

    def get_pseudo_color(self):
        limit_mask = self["Z"] < self.LIMIT_DEPTH
        depth = self["Z"] * limit_mask
        depth = depth / depth.max()
        depth[~limit_mask] = 1.1
        depth = 1 - depth
        return heatmap_to_pseudo_color(depth)

    def get_depth(self):
        # turn inf depth to 0
        limit_mask = self["Z"] < self.LIMIT_DEPTH
        depth = self["Z"] * limit_mask
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
        image = self["image"]
        depth_vis = self["_raw_exr"].get_pseudo_color()
        inst_vis = greyToRgb(histEqualize(self["inst"]))
        vis = (
            np.concatenate([inst_vis, image[..., :3] / 255.0, depth_vis], 1) * 255
        ).astype(np.uint8)
        return vis

    def save(self, dataset_dir="dataset", fname="0"):
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
        # save image at last for unstable compute enviroment
        if self.get("image") is not None:
            image_dir = pathjoin(dataset_dir, "image")
            os.makedirs(image_dir, exist_ok=True)
            image_path = pathjoin(image_dir, fname + ".jpg")
            cv2.imwrite(image_path, self["image"][..., ::-1])


def parser_exr(exr_path):
    file = OpenEXR.InputFile(exr_path)
    header = file.header()

    h, w = header["displayWindow"].max.y + 1, header["displayWindow"].max.x + 1
    exr = ExrDict()
    for key in header["channels"]:
        assert header["channels"][key].type.__str__() == "FLOAT"
        exr[key] = np.fromstring(file.channel(key), dtype=np.float32).reshape(h, w)
    file.close()
    return exr


def test_parser_exr(exr_path="../tmp_exrs/cycles.exr"):
    return parser_exr(exr_path)


if __name__ == "__main__":
    from boxx import show, imread

    exr_path = "tmp_exr.exr"
    exr_path = "../tmp_exrs/untitled.exr"
    exr_path = "/tmp/blender/tmp.exr"
    exr = parser_exr(exr_path)
    inst = exr.get_inst()
    png = imread(exr_path.replace(".exr", ".png"))[..., :3]

    ann = ImageWithAnnotation(png, exr)
    vis = ann.vis()
    show - vis
