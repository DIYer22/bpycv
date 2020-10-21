#!/usr/bin/env python3

import bpy
import bpycv

import os
import glob
import random
from pathlib import Path

example_data_dir = Path(
    os.path.abspath(os.path.join(__file__, "../../../bpycv_example_data"))
)

models = glob.glob(str(example_data_dir / "models" / "*" / "*.obj"))
cat_id_to_model_path = dict(enumerate(sorted(models), 1))

bpycv.clear_all()
bpy.context.scene.frame_set(1)
bpy.context.scene.render.engine = "CYCLES"
bpy.context.scene.cycles.samples = 32

stage = bpycv.add_stage(transparency=True)

bpycv.set_cam_pose(cam_radius=1, cam_deg=45)

hdri_dir = str(example_data_dir / "background_and_light")
hdri_manager = bpycv.HdriManager(hdri_dir=hdri_dir, download=False)
hdri_path = hdri_manager.sample()
bpycv.load_hdri_world(hdri_path, random_rotate_z=True)


for index in range(6):
    location = [random.random() * 1 - 0.5 for _ in range(3)]
    cat_id = random.choice(list(cat_id_to_model_path))
    model_path = cat_id_to_model_path[cat_id]
    obj = bpycv.load_obj(model_path)
    # set each instance a unique inst_id, which is used to generate instance annotation.
    obj["inst_id"] = cat_id * 1000 + index

    with bpycv.activate_obj(obj):
        bpy.ops.rigidbody.object_add()

for i in range(20):
    bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)

# render image, instance annoatation and depth in one line code
# result["ycb_meta"] is 6d pose GT
result = bpycv.render_data()
result.save(dataset_dir="/tmp/dataset", fname="0")

if __name__ == "__main__":
    from boxx import *
