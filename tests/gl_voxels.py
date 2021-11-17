# pyright: reportUnusedImport=false
from typing import Any
import __init__
import glm
import numpy as np
from source.data.colors import Colors
from source.interactive import Window
from source.utils.matrices import Hierarchy, OrbitCamera
from source.voxels.extra import vox_sphere
from source.voxels.proxy import VoxelProxy
from source.utils.types import int3
from source.utils.wireframe import Wireframe
from source.utils.mesh_loader import loadMeshes
from source.utils.directory import cwd, script_dir
from OpenGL.GL import *
from random import random, choice, randint


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


def rescale(shape: int3) -> glm.mat4:
    S: float = 1 / np.max(shape)  # type: ignore
    V = glm.vec3(S, S, S)
    return glm.scale(V)


class Voxels(Window):

    def setup(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.4, 0.4, 0.8, 1.0)
        self.matrices = Hierarchy()
        self.camera = OrbitCamera(
            distance=1.5,
            svivel_speed=0.005,
        )
        shape = (32, 32, 32)
        resolution = 2**10
        self.voxels = VoxelProxy(shape, resolution, {
            "blue": Colors.BLUE,
            "green": Colors.GREEN,
            "red": Colors.RED,
        })

        self.materials = self.voxels.material_list()
        self.addVoxels()
        self.wireframe()
        # Cache transforms

        # Translate to center of Voxel grid
        S: int = np.max(shape)  # type: ignore
        T = glm.vec3(shape) * (-0.5/S)
        self.t_vox = glm.translate(T)
        self.t_mesh = (
            rescale(shape) *
            glm.translate(glm.vec3(1, 1, 1) * -0.5)
        )
        self.t_bone = (
            glm.translate(glm.vec3(0, 0, -0.35)) *
            glm.scale(glm.vec3(0.17)) *
            glm.rotate(glm.pi() / 2, glm.vec3(1, 0, 0))
        )

        # Some internal state
        self.alphas = np.power([1.0, 0.75, 0.5, 0.25, 0.0], 4)  # type: ignore
        self.move_mode = False
        self.move_active = False

        # Bind camera controls
        self.keys.toggle("LEFT_CONTROL")(
            lambda press: setattr(self, 'move_mode', press))
        self.buttons.toggle("LEFT")(
            lambda press: setattr(self, 'move_active', press))
        # Bind alpha controls
        self.keys.action("U")(lambda: self.alpha(True))
        self.keys.action("I")(lambda: self.alpha(False))
        # Bind refresh controls
        self.keys.action("R")(lambda : self.wireframe())

        # Bind toggle outline
        self.keys.action("O")(self.voxels.toggle_outline)

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

    def alpha(self, up: bool):
        step = 1 if up else -1
        self.alphas: 'np.ndarray[np.float32]' = \
            np.roll(self.alphas, step)  # type: ignore
        self.voxels.set_alpha(self.alphas[0])

    _old: list[Any] = []

    def wireframe(self):
        if hasattr(self, 'mesh'):
            # TODO: fix !
            self._old.append(self.mesh)
        self.mesh = self.voxels.get_mesh(glm.vec4(0.8, 0.8, 1, 1))

    def resize(self, width: int, height: int):
        self.move_scale = 1 / max(width, height)
        glViewport(0, 0, width, height)
        self.matrices.SetPerspective(
            fovy=glm.radians(45.0),
            aspect=(width / height),
            near=0.01,
            far=100.0,
        )

    rng = np.random.default_rng()

    def addVoxels(self):
        material = choice(self.materials)
        shape = self.voxels.data.shape
        R = randint
        volume = tuple(R(4, 16) for _ in range(3))
        offset: int3 = \
            tuple(R(0, a - b) for a, b in zip(shape, volume))  # type: ignore
        strength: Any = \
            self.rng.random(size=volume, dtype=np.float32)  # type: ignore
        self.voxels.add_box(offset, strength + 0.5, material)

    def update(self, time: float, delta: float):
        # Debug w random voxels
        if random() * time < 2:
            self.addVoxels()

        # Update Camera Matrix
        self.matrices.V = self.camera.Compute()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
        M = self.matrices
        # Render Opaque first
        # with M.Push(self.t_bone):
        #    self.bone.render(self.matrices)
        with M.Push(self.t_vox):
            # Render mesh
            with M.Push(self.t_mesh):
                self.mesh.render(self.matrices)
            # Render Transparent last
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
    window.spin()
