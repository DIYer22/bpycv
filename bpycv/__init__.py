# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
bpycv: computer vision utils for Blender
"""
__version__ = "0.0.2"
__short_description__ = "Computer vision utils for Blender."
__license__ = "MIT"
__author__ = "DIYer22"
__author_email__ = "ylxx@live.com"
__maintainer__ = "DIYer22"
__maintainer_email__ = "ylxx@live.com"
__github_username__ = "DIYer22"
__github_url__ = "https://github.com/DIYer22/bpycv"
__support__ = "https://github.com/DIYer22/bpycv/issues"


from .exr_image_parser import parser_exr, ImageWithAnnotation
from .select_utils import bpy, scene, render, get_objdf
from .object_utils import activate_obj, remove_obj
from .material_utils import set_inst_map_material
from .render_utils import set_cycle_render, set_inst_map_render, render_data
