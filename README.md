# `bpycv`: computer vision and deep learning utils for Blender

### Contents: [Features](#-features) | [Install](#-install) | [Demo](#-demo) | [Tips](#-tips) 

![0](https://user-images.githubusercontent.com/10448025/115022704-55937980-9ef0-11eb-952e-c85eb5fad4b8.jpg)      
*Figure.1 Render instance annoatation, RGB image and depth*

## ▮ Features
 - [x] Render annotations for semantic segmentation, instance segmentation and panoptic segmentation 
 - [x] Generate 6DoF pose ground truth
 - [x] Render depth ground truth
 - [x] Pre-defined domain randomization: 
    - [Light and background](https://github.com/DIYer22/bpycv_example_data/tree/main/background_and_light), automatic download from [HDRI Haven](https://hdrihaven.com/hdris/)
    - [Distractors](https://arxiv.org/pdf/1804.06516) from [ShapeNet](https://shapenet.org/) (e.g. vase, painting, pallet in Figure.1)
    - Textures from [Texture Haven](https://texturehaven.com/textures/)
 - [x] Very easy to install and run demo
 - [x] Support docker: `docker run -v /tmp:/tmp diyer22/bpycv` (see [Dockerfile](Dockerfile))
 - [x] A [Python Codebase](example/ycb_demo.py) for building synthetic datasets
 - [x] To [Cityscapes annotation format](https://github.com/DIYer22/bpycv/issues/38)

**News:** [We win 🥈2nd place in IROS 2020 Open Cloud Robot Table Organization Challenge (OCRTOC)](https://github.com/DIYer22/bpycv/issues/15)

## ▮ Install
`bpycv` support Blender 2.8, 2.9, 3.0, 3.1+

```bash
# Get pip: equl to /blender-path/3.xx/python/bin/python3.10 -m ensurepip
blender -b --python-expr "import os,sys;os.system(f\"'{sys.executable}' -m ensurepip \")" 
# Update pip toolchain
blender -b --python-expr "import os,sys;os.system(f\"'{sys.executable}' -m pip install -U pip setuptools wheel \")" 
# pip install bpycv
blender -b --python-expr "import os,sys;os.system(f\"'{sys.executable}' -m pip install -U bpycv \")" 
# Check bpycv ready
blender -b -E CYCLES --python-expr 'import bpycv,boxx;boxx.tree(bpycv.render_data())'
```

## ▮ Demo
#### 1. Fast Instance Segmentation and Depth Demo
Copy-paste this code to `Scripting/Text Editor` and click `Run Script` button(or `Alt+P`)
```python
import cv2
import bpy
import bpycv
import random
import numpy as np

# remove all MESH objects
[bpy.data.objects.remove(obj) for obj in bpy.data.objects if obj.type == "MESH"]

for index in range(1, 20):
    # create cube and sphere as instance at random location
    location = [random.uniform(-2, 2) for _ in range(3)]
    if index % 2:
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=location)
        categories_id = 1
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=location)
        categories_id = 2
    obj = bpy.context.active_object
    # set each instance a unique inst_id, which is used to generate instance annotation.
    obj["inst_id"] = categories_id * 1000 + index

# render image, instance annoatation and depth in one line code
# result["ycb_meta"] is 6d pose GT
result = bpycv.render_data()

# save result
cv2.imwrite(
    "demo-rgb.jpg", result["image"][..., ::-1]
)  # transfer RGB image to opencv's BGR

# save instance map as 16 bit png
# the value of each pixel represents the inst_id of the object to which the pixel belongs
cv2.imwrite("demo-inst.png", np.uint16(result["inst"]))

# convert depth units from meters to millimeters
depth_in_mm = result["depth"] * 1000
cv2.imwrite("demo-depth.png", np.uint16(depth_in_mm))  # save as 16bit png

# visualization inst_rgb_depth for human
cv2.imwrite("demo-vis(inst_rgb_depth).jpg", result.vis()[..., ::-1])
```
Open `./demo-vis(inst_rgb_depth).jpg`:   

![demo-vis(inst_rgb_depth)](https://user-images.githubusercontent.com/10448025/115022679-4ad8e480-9ef0-11eb-9a42-cdfbf7e9d2ae.jpg)

#### 2. YCB Demo

```shell
mkdir ycb_demo
cd ycb_demo/

# prepare code and example data
git clone https://github.com/DIYer22/bpycv
git clone https://github.com/DIYer22/bpycv_example_data

cd bpycv/example/

blender -b -P ycb_demo.py

cd dataset/vis/
ls .  # visualize result here
# 0.jpg
```
Open visualize result `ycb_demo/bpycv/example/dataset/vis/0.jpg`:   
![0](https://user-images.githubusercontent.com/10448025/115022704-55937980-9ef0-11eb-952e-c85eb5fad4b8.jpg)    
*instance_map | RGB | depth*

[example/ycb_demo.py](example/ycb_demo.py) Inculding:
- Domain randomization for background, light and distractor (from ShapeNet)
- Codebase for building synthetic datasets base on YCB dataset

#### 3. 6DoF Pose Demo
Generate and visualize 6DoF pose GT: [example/6d_pose_demo.py](example/6d_pose_demo.py)

<img src="https://user-images.githubusercontent.com/10448025/74708759-5e3ee000-5258-11ea-8849-0174c34d507c.png" style="width:300px">


## ▮ Tips
 > Blender may can't direct load `.obj` or `.dea` file from YCB and ShapeNet dataset.  
 > It's better to transefer and format using [`meshlabserver`](https://github.com/cnr-isti-vclab/meshlab/releases) by run `meshlabserver -i raw.obj -o for_blender.obj -m wt`

<br>
<br>
<div align="center">

**[suggestion](https://github.com/DIYer22/bpycv/issues) and pull request are welcome** 😊
</div>