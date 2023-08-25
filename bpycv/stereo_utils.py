#!/usr/bin/env python3
import boxx
from boxx import np

with boxx.inpkg():
    from .camera_utils import get_cam_hw, set_cam, get_cam, get_cam_intrinsic
    from .render_utils import render_image, render_data
    from .pose_utils import set_pose_in_cam, T_bcam2cv
import cv2
import mathutils


class StereoCamera:
    def __init__(self, cam=None, R=(0, 0, 0.0), t=-0.062, cam1=None, cam2=None):
        """
        cam1/cam2: dict. left/right cam's intrinsic, like {"K": float64(3,3), "xy":[w,h]}
        Similar to stereo module, calibrating.Cam
        See: https://github.com/DIYer22/calibrating
        R: np.array with shape (3,) or (3, 3). Rotation matrix.
        t: float or shape (3,).

        Different to Blender stereocopy's "Stereo 3D" and "multi-view":
        - Close to the real 6D degree of freedom
        - More closely combined with opencv's stereo
        """
        import calibrating  # by pip install calibrating

        t = np.array(t)
        if t.size == 1:
            t = np.array([t, 0.0, 0])
        R = np.array(R)
        if R.size == 3:
            R = cv2.Rodrigues(np.float64(R))[0]
        T_cam1_in_cam2 = calibrating.R_t_to_T(R, t)
        self.T_cam2_in_cam1 = np.linalg.inv(T_cam1_in_cam2)
        self.cam = get_cam(cam)

        cam1 = cam1 or {}
        cam1.setdefault("K", get_cam_intrinsic(self.cam))
        cam1.setdefault("xy", get_cam_hw()[::-1])
        cam2 = cam2 or cam1.copy()

        self.cam1 = cam1
        self.cam2 = cam2

        self.cam_right = self.get_cam_right()
        set_cam(self.cam, K=self.cam1["K"], hw=self.cam1["xy"][::-1])
        self.cam["stereo_camera_id"] = self.cam_right["stereo_camera_id"] = str(
            id(self)
        )

    def get_cam_right(self):
        name = self.cam.name
        name_right = name + "_R"
        if name.endswith("_L"):
            name_right = name[:-2] + "_R"
        matrix_world = (self.cam.matrix_world) @ mathutils.Matrix(
            T_bcam2cv @ self.T_cam2_in_cam1
        )
        # cam_right = set_cam(name_right, K=self.cam2["K"], hw=self.cam2["xy"][::-1])
        # set_pose_in_cam(cam_right, self.T_cam2_in_cam1@T_bcam2cv, self.cam)
        # return cam_right
        return set_cam(name_right, matrix_world, self.cam2["K"], self.cam2["xy"][::-1])

    def render_image(self):

        imgd = dict(image1=render_image(self.cam))
        self.cam_right = self.get_cam_right()
        imgd["image2"] = render_image(self.cam_right)
        set_cam(self.cam, K=self.cam1["K"], hw=self.cam1["xy"][::-1])
        return imgd

    def render_data(self, render_annotation=True):
        imgd = self.render_image()
        data = render_data(render_image=False, render_annotation=render_annotation)
        data["image1"] = imgd["image1"]
        data["image2"] = imgd["image2"]
        # TODO
        # return and save Disparity + rectify_img1 rectify_img2 + calibrating.yaml
        return data

    @classmethod
    def from_calibrating(cls, path_or_str_or_dict=None, cam=None):
        import calibrating

        stereo = calibrating.Stereo.load(path_or_str_or_dict)
        dic = stereo.dump(return_dict=True)
        dic["cam1"]["K"] = calibrating.intrinsic_format_conversion(dic["cam1"])
        dic["cam2"]["K"] = calibrating.intrinsic_format_conversion(dic["cam2"])
        self = cls(cam=cam, R=dic["R"], t=dic["t"], cam1=dic["cam1"], cam2=dic["cam2"])
        self.cam["stereo_calibrating"] = dic
        return self


if __name__ == "__main__":
    from boxx import *

    stereo_cam = StereoCamera(t=[-0.2, 0, 0.02])
    imgd = stereo_cam.render_image()
    boxx.tree / imgd
    # import IPython
    # IPython.embed()

    # blender -b -P bpycv/stereo_utils.py
