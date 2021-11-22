# pyright: reportUnusedImport=false
from typing import Any, cast
import __init__
import glm
import numpy as np
from source.data.colors import Colors
from source.interactive import Window
from source.utils.matrices import Hierarchy, OrbitCamera
from source.utils.misc import random_box
from source.voxels.proxy import VoxelProxy
from source.utils.types import int3
from source.utils.wireframe import Wireframe, origin
from source.utils.mesh_loader import loadMeshes
from source.utils.directory import cwd, script_dir
from OpenGL.GL import *
from random import random, choice



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
            distance=1.25,
            svivel_speed=0.005,
        )
        shape = (256, 256, 256)
        resolution = 2**10
        self.voxels = VoxelProxy(shape, resolution, {
            "blue": Colors.BLUE,
            "green": Colors.GREEN,
            "red": Colors.RED,
            "gray" : Colors.GRAY,
        })

        self.materials = self.voxels.material_list()
        for _ in range(1):
            self.addVoxels()
        self.wireframe()

        self.origin = Wireframe(origin(0.05), glm.vec4(1, 0.5, 0, 1), 1.0)

        # Cache transforms

        # Normalze Voxel grid (0 -> N) => (0.0 -> 1.0) 
        self.t_norm = glm.scale(glm.vec3(1/max(*shape)))
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
        self.keys.action("R")(self.wireframe)

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

    def alpha(self, up: bool):
        step = 1 if up else -1
        self.alphas: 'np.ndarray[np.float32]' = \
            np.roll(self.alphas, step)  # type: ignore
        self.voxels.set_alpha(self.alphas[0])

    def wireframe(self):
        print("[Mesh] Building")
        try:
            self.truss = self.voxels.get_mesh(glm.vec4(0.8, 0.8, 1, 1))
            print("[Mesh] Done")
        except AssertionError as e:
            print("[Mesh] Assertion")
            print(e)
        except Error as e:
            print("[Mesh] Error")
            print(e)

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
        voxels = self.voxels
        volume, offset = random_box(voxels.data.shape, 32, 32)
        strength: Any = \
            self.rng.random(size=volume, dtype=np.float32)  # type: ignore
        voxels.add_box(offset, strength - 0.35, choice(self.materials))  # type: ignore

    def update(self, time: float, delta: float):
        # Debug w random voxels
        if random() * time < 0.5:
            self.addVoxels()

        # Update Camera Matrix
        self.matrices.V = self.camera.Compute()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
        M = self.matrices
        # Render Opaque first

        # Render origin when navigating
        if self.move_active:
            with M.Push(glm.translate(self.camera.center)):
                self.origin.render(M)

        # with M.Push(self.t_bone):
        #    self.bone.render(self.matrices)

        with M.Push(self.t_norm):

            # Render Truss mesh
            self.truss.render(M)

            # Render Transparent last
            self.voxels.render(M)

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
