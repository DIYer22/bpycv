# -*- coding: utf-8 -*-
"""
bpycv: computer vision utils for Blender
    https://github.com/DIYer22/bpycv
"""

from .__info__ import __version__

from .utils import ipython
from .hdri_manager import HdriManager
from .node_graph import activate_node_tree, Node
from .exr_image_parser import parser_exr

from .select_utils import bpy, scene, render, cam, world, get_objdf
from .statu_recover import undo
from .object_utils import (
    activate_obj,
    remove_obj,
    edit_mode,
    subdivide,
    duplicate,
    load_obj,
)
from .material_utils import set_inst_material, load_hdri_world, build_tex
from .render_utils import (
    set_cycles_compute_device_type,
    set_image_render,
    set_annotation_render,
    render_image,
    render_data,
)
from .pose_utils import get_6d_pose
from .scene_setting import (
    set_cam_pose,
    set_cam_intrinsic,
    remove_useless_data,
    clear_all,
    set_shading_mode,
    add_stage,
)
from .physic_utils import set_origin_and_record_old_v0
from .domain_randomzition import texture_bsdf_dr, load_distractor
