# `bpycv`: computer vision utils for Blender

![demo-vis(inst|rgb|depth).jpg](doc/img/demo-vis(inst|rgb|depth).jpg)    
*render instance annoatation, RGB image and depth in one line code*

## Features

 - [x] render depth
 - [x] render annotations for instance segmentation and panoptic segmentation 
 - [x] to cityscape format
 - [ ] to coco format
 - [ ] pre-define domain randomization

## Install
`bpycv` support Blender 2.8+

### 1. install OpenExr
`bpycv` use OpenExr to extract depth map from Blender

For a Debian-based Linux(Ubuntu):
```bash
sudo apt-get install libopenexr-dev
```

For other OS, please follow [OpenExr's instruction](https://excamera.com/sphinx/articles-openexr.html).

### 2. install python package
Example for Blender 2.81:
```bash
cd <path to blender>/2.81/python/bin
./python3.7m -m ensurepip  # get pip
./python3.7m -m pip install --upgrade pip setuptools wheel
./python3.7m -m pip install bpycv opencv-python
```

## Fast Demo

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
result = bpycv.render_data()

# save result
cv2.imwrite("demo-rgb.jpg", result["image"])
cv2.imwrite("demo-inst.png", result["inst"])
# normalizing depth
cv2.imwrite("demo-depth.png", result["depth"] / result["depth"].max() * 255)

# visualization inst|rgb|depth for human
cv2.imwrite("demo-vis(inst|rgb|depth).jpg", result.vis())
```
Open `./demo-vis(inst|rgb|depth).jpg`:   

![demo-vis(inst|rgb|depth).jpg](doc/img/demo-vis(inst|rgb|depth).jpg)

## Tips
 * Right now (Blender 2.81), using Eevee engine will raise Exception("Unable to open a display") when the enviroment not support GUI.