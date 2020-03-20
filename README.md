# `bpycv`: computer vision and deep learning utils for Blender

### Contents: [Features](#-features) | [Install](#-install) | [Fast Demo](#-fast-demo) | [Tips](#-tips) 

![demo-vis(inst|rgb|depth).jpg](doc/img/demo-vis(inst|rgb|depth).jpg)    
*render instance annoatation, RGB image and depth in one line code*

## ▮ Features
 - [x] render depth
 - [x] render annotations for instance segmentation and panoptic segmentation 
 - [x] generate 6DoF pose GT
 - [x] pre-define domain randomization: enviroment
 - [x] pre-define domain randomization: textures
 - [x] to cityscape format
 - [ ] to coco format

## ▮ Install
`bpycv` support Blender 2.8+

#### 1. Install OpenExr
`bpycv` use OpenExr to extract depth map from Blender

For a Debian-based Linux(Ubuntu):
```bash
sudo apt-get install libopenexr-dev
```

For other OS, please follow [OpenExr's instruction](https://excamera.com/sphinx/articles-openexr.html).

#### 2. Install python package
Example for Blender 2.81:
```bash
cd <path to blender>/2.81/python/bin
./python3.7m -m ensurepip  # get pip
./python3.7m -m pip install --upgrade pip setuptools wheel
./python3.7m -m pip install bpycv opencv-python
```

## ▮ Fast Demo
#### 1. Instance Segmentation and Depth Demo
Copy-paste this code to `Text Editor` and click `Run Script` button(or `Alt+P`)
```python
import cv2
import bpy
import bpycv
import random

# remove all MESH objects
[bpy.data.objects.remove(obj) for obj in bpy.data.objects if obj.type == "MESH"]

for inst_id in range(1, 20):
    # create cube and sphere as instance at random location
    location = [random.random() * 4 - 2 for _ in range(3)]
    if inst_id % 2:
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=location)
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.5, location=location)
    obj = bpy.context.active_object
    # set each instance a unique inst_id, which is used to generate instance annotation.
    obj["inst_id"] = inst_id

# render image, instance annoatation and depth in one line code
# result["ycb_meta"] is 6d pose GT
result = bpycv.render_data()

# save result
cv2.imwrite(
    "demo-rgb.jpg", cv2.cvtColor(result["image"], cv2.COLOR_RGB2BGR)  # cover RGB to BGR
)
cv2.imwrite("demo-inst.png", result["inst"])
# normalizing depth
cv2.imwrite("demo-depth.png", result["depth"] / result["depth"].max() * 255)

# visualization inst|rgb|depth for human
cv2.imwrite(
    "demo-vis(inst|rgb|depth).jpg", cv2.cvtColor(result.vis(), cv2.COLOR_RGB2BGR)
)
```
Open `./demo-vis(inst|rgb|depth).jpg`:   

![demo-vis(inst|rgb|depth).jpg](doc/img/demo-vis(inst|rgb|depth).jpg)


#### 2. 6DoF Pose Demo
<img src="https://user-images.githubusercontent.com/10448025/74708759-5e3ee000-5258-11ea-8849-0174c34d507c.png" style="width:300px">

Generate and visualize 6DoF pose GT: [example/6d_pose_demo.py](example/6d_pose_demo.py)


#### 3. Domain Randomization Demo

To be done....

## ▮ Tips
 * Right now (Blender 2.81), using Eevee engine will raise Exception("Unable to open a display") when the enviroment not support GUI.

<br>
<br>
<div align="center">

**[suggestion](https://github.com/DIYer22/bpycv/issues) and pull request are welcome** 😊
</div>