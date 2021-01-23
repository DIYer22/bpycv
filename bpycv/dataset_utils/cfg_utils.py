#!/usr/bin/env python3
import os
import sys
import argparse
from zcs import argument, ints
from zcs.config import CfgNode as CN


cfg = CN()
cfg.DIR = argument("/tmp/syn_dataset", str, "Generated dataset dir.")
cfg.IMG_NUM = argument(500, int, "How many number of images to generate?")
cfg.OBJ_NUM_DIST = argument(
    [2, 3, 3, 4], ints, "List to reveal distribution of objcts number per scene."
)
cfg.RESOLUTION = argument([1024, 1024], ints, "Height and width of image.")

cfg.DEBUG = False
cfg.MAX_INST = argument(1000, int, "Max instance number per category in one image.")


def get_default_cfg():
    return cfg.clone()


def get_arguments():
    parser = argparse.ArgumentParser(description="Build synthetic dataset by bpycv")
    parser.add_argument("--config", type=str, default=None, help="config file path")
    parser.add_argument(
        "opts",
        help="Modify config options using the command-line",
        default=None,
        nargs=argparse.REMAINDER,
    )
    argv_for_py = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    args = parser.parse_args(argv_for_py)
    return args


if __name__ == "__main__":
    from boxx import tree

    args = get_arguments()
    cfg = get_default_cfg()
    cfg.merge_from_list_or_str(args.opts)
    tree(cfg)
