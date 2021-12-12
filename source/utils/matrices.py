# pyright: reportConstantRedefinition=false
from dataclasses import dataclass
from contextlib import contextmanager
import glm
from glm_typing import F32Vector3
import numpy as np

I = glm.mat4()
Vec = F32Vector3


@dataclass
class Hierarchy:
    M: glm.mat4 = I
    V: glm.mat4 = I
    P: glm.mat4 = I

    @property
    def MV(self) -> glm.mat4:
        return self.V * self.M

    @property
    def MVP(self) -> glm.mat4:
        return self.P * self.V * self.M

    @contextmanager
    def Push(self, m: glm.mat4):
        M = self.M
        try:
            self.M = m * M
            yield
        finally:
            self.M = M
    
    def SetPerspective(self, fovy: float, aspect: float, near: float, far: float):
        self.P = glm.perspective(fovy, aspect, near, far)

    def SetLookAt(self, eye: Vec, center: Vec, up: Vec):
        self.V = glm.lookAt(eye, center, up)

    def GetCameraPosition(self) -> glm.vec3:
        I = glm.affineInverse(self.MV)
        return glm.vec3(I[3])

    def GetCameraDirection(self) -> glm.vec3:
        D = glm.affineInverse(self.MV)
        return glm.vec3(D[2])

    BUFFER_MATRIX = np.zeros((4, 4), dtype=np.float32)

    @classmethod
    def ptr(cls, m: glm.mat4):
        # Current correct matrix ptr, when passing to shaders
        cls.BUFFER_MATRIX[...] = m
        return cls.BUFFER_MATRIX

    @classmethod
    def copy(cls, m: glm.mat4):
        return cls.ptr(m).copy()


@dataclass
class OrbitCamera:
    up = glm.vec3(0, 0, 1)
    center: glm.vec3 = glm.vec3()
    h_angle: float = 0.0
    v_angle: float = 0.0
    distance: float = 1.0
    svivel_speed: float = 1.0
    move_speed: float = 0.001

    @property
    def dir(self):
        V = glm.vec2(self.h_angle, self.v_angle)
        h_s, v_s = glm.sin(V)
        h_c, v_c = glm.cos(V)
        return glm.vec3(v_c * h_s, v_c * h_c, v_s)

    def Svivel(self, h_delta: float, v_delta: float):
        # Adjust angles with camera speed
        self.h_angle += self.svivel_speed * h_delta
        self.v_angle += self.svivel_speed * v_delta

        # Constants
        PI = glm.pi()
        H_PI = PI / 2

        # Loop angle between (PI & -PI)
        if (self.h_angle > PI):
            self.h_angle -= 2 * PI
        elif (self.h_angle < -PI):
            self.h_angle += 2 * PI

        # Clamp angle inside of (H_PI & -H_PI)
        if (self.v_angle >= H_PI):
            self.v_angle = H_PI - 0.001
        elif (self.v_angle <= -H_PI):
            self.v_angle = 0.001 - H_PI

    def Move(self, dx: float, dy: float):
        D = self.dir
        U = self.up
        X = glm.normalize(glm.cross(D, U))
        Y = glm.normalize(glm.cross(X, D))
        M = X * dx + Y * dy
        S = self.move_speed * self.distance
        self.center += M * S

    def Zoom(self, amount: float):
        self.distance -= amount * np.log10(1 + self.distance * 0.05)
        e = 1E-10
        if self.distance < e:
            self.distance = e

    def Compute(self):
        eye = self.center + self.dir * self.distance
        return glm.lookAt(eye, self.center, self.up)
