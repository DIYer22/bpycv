#!/usr/bin/env python3

from boxx import *
from boxx import deg2rad, np, pi

import bpy
import random
import mathutils


def get_cams():
    return [obj for obj in bpy.data.objects if obj.type == "CAMERA"]


def get_cam(cam=None):
    """
    cam: Camera or str, if is str bpy.data.get(str, camera_add())
    """
    if cam is None:
        cam = bpy.context.scene.camera
    if isinstance(cam, str):
        name = cam
        if name not in bpy.data.objects:
            current_obj = bpy.context.view_layer.objects.active
            bpy.ops.object.camera_add()
            assert len(bpy.context.selected_objects) >= 1, f"Camera_add() failed!"
            cam = bpy.context.selected_objects[-1]
            cam.name = name
            bpy.context.view_layer.objects.active = current_obj
        cam = bpy.data.objects[name]
    return cam


def set_cam_pose(cam_radius=1, cam_deg=45, cam_x_deg=None, cam=None):
    """
    Set the camera pose according to the shape of hemisphere.

    Parameters
    ----------
    cam_radius : float, optional
        The distance of the camera from the origin 0,0,0. The default is 1m.
    cam_deg : float, optional
        The angle between the optical center and the XY-plane. The default is 45°.
    cam_x_deg : float, optional
        The angle between the optical center and the X-axis. The default is None.
    cam : Camera object, optional
        The default is first camera object.

    Returns
    -------
    cam : Camera object
    """
    cam_rad = deg2rad(cam_deg)
    if cam_x_deg is None:
        cam_x_deg = random.uniform(0, 360)
    cam_x_rad = deg2rad(cam_x_deg)
    z = cam_radius * np.sin(cam_rad)
    xy = (cam_radius**2 - z**2) ** 0.5
    x = xy * np.cos(cam_x_rad)
    y = xy * np.sin(cam_x_rad)
    cam = get_cam(cam)
    cam.location = x, y, z
    cam.rotation_euler = pi / 2 - cam_rad, 0.0, pi / 2 + cam_x_rad
    # cam.scale = (cam_radius * 0.1,) * 3
    return cam


def get_cam_hw(cam=None):
    render = bpy.context.scene.render
    return render.resolution_y, render.resolution_x


def get_cam_intrinsic(cam=None):
    """
    Refrence:
        https://blender.stackexchange.com/a/120063/86396
    """
    # BKE_camera_sensor_size
    def get_sensor_size(sensor_fit, sensor_x, sensor_y):
        if sensor_fit == "VERTICAL":
            return sensor_y
        return sensor_x

    # BKE_camera_sensor_fit
    def get_sensor_fit(sensor_fit, size_x, size_y):
        if sensor_fit == "AUTO":
            if size_x >= size_y:
                return "HORIZONTAL"
            else:
                return "VERTICAL"
        return sensor_fit

    cam = get_cam(cam)
    camd = cam.data
    if camd.type != "PERSP":
        raise ValueError("Non-perspective cameras not supported")
    scene = bpy.context.scene
    f_in_mm = camd.lens
    scale = scene.render.resolution_percentage / 100
    resolution_x_in_px = scale * scene.render.resolution_x
    resolution_y_in_px = scale * scene.render.resolution_y
    sensor_size_in_mm = get_sensor_size(
        camd.sensor_fit, camd.sensor_width, camd.sensor_height
    )
    sensor_fit = get_sensor_fit(
        camd.sensor_fit,
        scene.render.pixel_aspect_x * resolution_x_in_px,
        scene.render.pixel_aspect_y * resolution_y_in_px,
    )
    pixel_aspect_ratio = scene.render.pixel_aspect_y / scene.render.pixel_aspect_x
    if sensor_fit == "HORIZONTAL":
        view_fac_in_px = resolution_x_in_px
    else:
        view_fac_in_px = pixel_aspect_ratio * resolution_y_in_px
    pixel_size_mm_per_px = sensor_size_in_mm / f_in_mm / view_fac_in_px
    s_u = 1 / pixel_size_mm_per_px
    s_v = 1 / pixel_size_mm_per_px / pixel_aspect_ratio

    # Parameters of intrinsic calibration matrix K
    u_0 = resolution_x_in_px / 2 - camd.shift_x * view_fac_in_px
    v_0 = resolution_y_in_px / 2 + camd.shift_y * view_fac_in_px / pixel_aspect_ratio
    skew = 0  # only use rectangular pixels

    K = mathutils.Matrix(((s_u, skew, u_0), (0, s_v, v_0), (0, 0, 1)))
    return K


def set_cam_intrinsic(cam, K, hw=None):
    """
    change cam and K
    Invert the function get_cam_intrinsic

    K =[[s_u, 0, u_0],
        [0, s_v, v_0],
        [0,   0,   1]]
    or
    K =[[f_x, 0, c_x],
        [0, f_y, c_y],
        [0,   0,   1]]
    """
    scene = bpy.context.scene
    camd = cam.data
    camd.sensor_fit = "HORIZONTAL"
    camd.sensor_width = 10
    scene.render.resolution_percentage = 100

    if hw is None:
        hw = scene.render.resolution_y, scene.render.resolution_x
    else:
        scene.render.resolution_y, scene.render.resolution_x = hw
    near = lambda x, y=0, eps=1e-5: abs(x - y) < eps
    assert near(K[0][1], 0)
    assert near(K[1][0], 0)

    h, w = hw
    s_u = K[0][0]  # f_x
    s_v = K[1][1]  # f_y
    u_0 = K[0][2]  # c_x
    v_0 = K[1][2]  # c_y
    scene.render.pixel_aspect_x = s_v / min(s_u, s_v)
    scene.render.pixel_aspect_y = s_u / min(s_u, s_v)
    pixel_aspect_ratio = s_u / s_v
    camd.lens = s_u * camd.sensor_width / w
    camd.shift_x = (w / 2 - u_0) / w
    camd.shift_y = (v_0 - h / 2) / w * pixel_aspect_ratio


def set_cam(cam=None, matrix_world=None, K=None, hw=None):
    """
    cam: Camera or str, will get_cam(cam)
    matrix_world: 4x4 matrix world
    K: 3x3 intrinsic
    hw: tuple
    """
    from .pose_utils import set_matrix_world

    cam = get_cam(cam)
    if matrix_world is not None:
        set_matrix_world(
            cam,
            matrix_world
            @ mathutils.Matrix(
                ((1, 0, 0, 0), (0, -1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1))
            ),
        )
    if K is not None:
        set_cam_intrinsic(cam, K, hw)
    return cam


if __name__ == "__main__":
    pass
