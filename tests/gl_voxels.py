import __init__
import glm
import numpy as np
from source.interactive import Window
from source.utils.matrices import Hierarchy, OrbitCamera
from source.voxels.extra import vox_sphere
from source.voxels.mesh_loader import loadMeshes
from source.voxels.render import VoxelGrid
from source.voxels.wireframe import Wireframe
from source.utils.directory import cwd, script_dir
from OpenGL.GL import *
from random import random


"""
TODO:

1. Triangle intersection:
    https://courses.cs.washington.edu/courses/csep557/10au/lectures/triangle_intersection.pdf

2. Mesh Loader
    use .obj to load

3. Mesh to Voxels

"""

@cwd(script_dir(__file__), '..', 'meshes')
def bone():
    BONE, = loadMeshes('test_bone.obj')
    return BONE


class Voxels(Window):

    def setup(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.4, 0.4, 0.8, 1.0)
        self.matrices = Hierarchy()
        self.camera = OrbitCamera(
            distance=1.5,
            svivel_speed=0.005,
        )
        shape = (128, 128, 128)
        resolution = 2**8
        self.voxels = VoxelGrid(shape, resolution)

        # Cache transforms

        # Translate to center of Voxel grid
        S: int = np.max(shape)  # type: ignore
        T = glm.vec3(shape) * (-0.5/S)
        self.t_vox = glm.translate(T)
        self.t_bone = (
            glm.translate(glm.vec3(0, 0, -0.35)) *
            glm.scale(glm.vec3(0.17)) *
            glm.rotate(glm.pi() / 2, glm.vec3(1, 0, 0))
        )

        # Some internal state
        self.alpha_up = False
        self.alpha_dn = False
        self.move_mode = False
        self.move_active = False

        # Bind camera controls
        self.keys.toggle("LEFT_CONTROL")(
            lambda press: setattr(self, 'move_mode', press))
        self.buttons.toggle("LEFT")(
            lambda press: setattr(self, 'move_active', press))
        # Bind alpha controls
        self.keys.toggle("U")(lambda press: setattr(self, 'alpha_up', press))
        self.keys.toggle("I")(lambda press: setattr(self, 'alpha_dn', press))

        # TODO: async load
        """
        self.bone = Wireframe(
            bone(),
            glm.vec4(0.8, 0.8, 1, 1),
            2.0,
        )
        """

        # Display fancy volumetric sphere
        # vox_sphere(self.voxels)

    def resize(self, width: int, height: int):
        self.move_scale = 1 / max(width, height)
        glViewport(0, 0, width, height)
        self.matrices.SetPerspective(
            fovy=glm.radians(45.0),
            aspect=(width / height),
            near=0.01,
            far=100.0,
        )

    def alpha_step(self) -> float:
        a = self.voxels.alpha
        c = 1.0 - 2.0 * abs(a - 0.5)
        o = c * c
        return o * 2.0

    def update(self, time: float, delta: float):
        # Debug w ranom voxels
        if random() * time < 1:
            S: int = np.min(self.voxels.shape) // 2  # type: ignore
            self.voxels.randBox(S)

        # Modify alpha
        if self.alpha_up == self.alpha_dn:
            pass
        elif self.alpha_up:
            self.voxels.alpha += self.alpha_step() * delta
        elif self.alpha_dn:
            self.voxels.alpha -= self.alpha_step() * delta

        # Update Camera Matrix
        self.matrices.V = self.camera.Compute()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
        M = self.matrices
        # Render Opaque first
        #with M.Push(self.t_bone):
        #    self.bone.render(self.matrices)
        # Render Transparent last
        with M.Push(self.t_vox):
            self.voxels.render(self.matrices)
        # TODO: post process with gaussian blur ?

    def move(self, dx: float, dy: float):
        if self.move_mode:
            # Move Position
            self.camera.Move(dx, dy)

        else:
            # Move Camera
            self.camera.Svivel(dx, dy)

    def cursor(self, x: float, y: float, dx: float, dy: float):
        if self.move_active:
            self.move(dx, dy)

    def scroll(self, value: float):
        self.camera.Zoom(value)


if __name__ == '__main__':
    size = 900
    window = Voxels(size, size, "voxels")

    @window.keys.action("B")
    def cube():
        window.voxels.randBox()

    @window.keys.action("O")
    def outline():
        window.voxels.outline = not window.voxels.outline

    window.spin()
