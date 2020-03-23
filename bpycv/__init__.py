# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
bpycv: computer vision utils for Blender
"""
__version__ = "0.2.11"
__short_description__ = "Computer vision utils for Blender."
__license__ = "MIT"
__author__ = "DIYer22"
__author_email__ = "ylxx@live.com"
__maintainer__ = "DIYer22"
__maintainer_email__ = "ylxx@live.com"
__github_username__ = "DIYer22"
__github_url__ = "https://github.com/DIYer22/bpycv"
__support__ = "https://github.com/DIYer22/bpycv/issues"


from .utils import ipython
from .hdri_manager import HdriManager
from .node_graph import activate_node_tree, Node
from .exr_image_parser import parser_exr

from .select_utils import bpy, scene, render, cam, world, get_objdf
from .statu_recover import undo
from .object_utils import activate_obj, remove_obj, edit_mode, subdivide, duplicate
from .material_utils import set_inst_material, load_hdri_world, build_tex
from .render_utils import set_image_render, set_annotation_render, render_data
from .pose_utils import get_6d_pose
from .scene_setting import (
    set_cam_pose,
    remove_useless_data,
    clear_all,
    set_shading_mode,
)
