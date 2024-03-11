## Star History

![Star History Chart](https://api.star-history.com/svg?repos=diyer22/bpycv,DLR-RM/BlenderProc,ZumoLabs/zpy,google-research/kubric&type=Date)

## TODO
- [ ] stereo.render_data() return Disparity, .etc
- [ ] texturehaven's version of HdriManager
- [ ] demo for build_tex and hdri
- [ ] better instance map: which consider displacement
    - [ ] better instance map: by pass.object_index and compositing
    - https://github.com/DIYer22/bpycv/issues/27
    - https://cgcooke.github.io/Blog/computer%20vision/blender/2020/10/23/Synthetic-Training-Data-With-Blender.html
- [ ] a better 6d pose format
- [ ] visualize 3d bounding box of 6DoF GT(How to set xyzs)
- [ ] answer first result of google: "blender depth python"
- [ ] sample obj/camera location according to size info
- [ ] to COCO format
    - by cv_data
- [ ] make better demo images by `img_switch_special_effect.js`
- [ ] difference with:
    - https://github.com/DLR-RM/BlenderProc
    - https://github.com/Cartucho/vision_blender
    - https://github.com/cheind/pytorch-blender
    - https://github.com/kopernikusai/shapes3d
    - https://github.com/ZumoLabs/zpy
    - https://developer.nvidia.com/isaac-sim
    - https://github.com/google-research/kubric

## Done
- [x] fix wrong depth bug by CYCLES
- [ ] ~~support blender's Stereoscopy~~(Stereo by `StereoCamera`)
    - https://docs.blender.org/manual/en/latest/render/output/properties/stereoscopy/index.html
- [x] obj size info
- [x] support blender 3.0+
- [x] document and tutorial
- [x] support docker
- [x] add `camera_utils.py` with `set/get_cam_intrinsic`
- [x] project example: YCB model example
- [x] pre-define distractor
- [x] pre-define domain randomization: texture
- [x] ImageWithAnnotation.save()
- [x] `cv2.imwrite` change to rgb channel, in demo code
- [x] pre-define domain randomization: hdri
- [x] use `bpy.ops.ed.undo_push` to undo
- [ ] ~~detect whether in ssh X11 forward in annotation_render~~
- [x] figure out length unit in Blender
- [x] add generate_and_visualize_cube_6d_pose_demo.py
- [x] figure out and generate 6DoF GT
- [x] statu_recover in with statment
- [x] render annotations for instance segmentation
- [x] render depth
