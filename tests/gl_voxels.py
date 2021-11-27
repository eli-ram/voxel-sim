# pyright: reportUnusedImport=false
from typing import Any
import __init__
import glm
import numpy as np
from source.data.colors import Colors
from source.debug.time import time
from source.interactive import Window
from source.utils.matrices import Hierarchy, OrbitCamera
from source.utils.misc import random_box
from source.utils.wireframe import Wireframe, line_cube, origin, simplex
from source.utils.mesh_loader import loadMeshes
from source.utils.directory import cwd, script_dir
from source.math.mesh2voxels import mesh_2_voxels
from source.voxels.proxy import VoxelProxy
from OpenGL.GL import *
from random import random, choice


"""
TODO:

1. Triangle intersection:

2. Mesh Loader
    use .obj to load

3. Mesh to Voxels

"""


@cwd(script_dir(__file__), '..', 'meshes')
@time("BONE")
def bone():
    BONE, = loadMeshes('test_bone.obj')
    return BONE


class Voxels(Window):

    def setup(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.4, 0.4, 0.8, 1.0)
        self.matrices = Hierarchy()
        self.camera = OrbitCamera(
            distance=1.25,
            svivel_speed=0.005,
        )
        shape = (128, 128, 128)
        resolution = 2**11
        self.voxels = VoxelProxy(shape, resolution, {
            "blue": Colors.BLUE,
            "green": Colors.GREEN,
            "red": Colors.RED,
            "gray": Colors.GRAY,
        })

        self.materials = self.voxels.material_list()

        # 3D-crosshair for camera
        self.origin = Wireframe(origin(0.05), glm.vec4(1, 0.5, 0, 1), 1.0)

        # Outline for Voxels
        self.cube = Wireframe(line_cube(), glm.vec4(0, 0, 0, 1), 1.0)

        # Bone Model
        # TODO: async load
        self.bone_mesh = bone()
        # self.bone_mesh = simplex()
        self.bone = Wireframe(
            self.bone_mesh,
            glm.vec4(0.8, 0.8, 1, 1),
            2.0,
        )

        # Cache transforms

        # Normalze Voxel grid (0 -> N) => (0.0 -> 1.0)
        self.t_norm = glm.scale(glm.vec3(1/max(*shape)))
        self.t_bone = (
            glm.translate(glm.vec3(0.5, 0.5, -0.5)) *
            glm.scale(glm.vec3(0.3)) *
            glm.translate(glm.vec3(0, 0, 0.1)) * 
            glm.rotate(glm.pi() / 2, glm.vec3(1, 0, 0))
        )
        """
        self.t_bone = (
            glm.translate(glm.vec3(0.2)) *
            glm.scale(glm.vec3(0.8))
        )
        """

        # Some internal state
        self.alphas = np.power([1.0, 0.75, 0.5, 0.25, 0.0], 4)  # type: ignore
        self.move_mode = False
        self.move_active = False
        self.show_bone = True

        # Toggle Bone
        self.keys.action("H")(lambda: setattr(self, 'show_bone', not self.show_bone))

        # Bind camera controls
        self.keys.toggle("LEFT_CONTROL")(
            lambda press: setattr(self, 'move_mode', press))
        self.buttons.toggle("LEFT")(
            lambda press: setattr(self, 'move_active', press))

        # Bind alpha controls
        self.keys.action("U")(lambda: self.alpha(True))
        self.keys.action("I")(lambda: self.alpha(False))

        # Bind toggle outline
        self.keys.action("O")(self.voxels.toggle_outline)

        # Bind other controls
        self.keys.action("R")(self.wireframe)
        self.keys.action("B")(self.get_bone_voxels)

    def alpha(self, up: bool):
        step = 1 if up else -1
        self.alphas: 'np.ndarray[np.float32]' = \
            np.roll(self.alphas, step)  # type: ignore
        self.voxels.set_alpha(self.alphas[0])

    @time("Mesh")
    def wireframe(self):
        self.truss = self.voxels.get_mesh(glm.vec4(0.8, 0.8, 1, 1))

    @time("Voxels")
    def get_bone_voxels(self):
        t = glm.affineInverse(self.t_norm) * self.t_bone
        t = self.matrices.ptr(t)[:3, :]
        g = mesh_2_voxels(self.bone_mesh, t, self.voxels.data.shape, "Y")
        self.voxels.add_box((0, 0, 0), g.astype(np.float32), "red")

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
        material = choice(self.materials)
        voxels.add_box(offset, strength - 0.35, material)
        
    def update(self, time: float, delta: float):
        # Debug w random voxels
        if random() * time < 0:
            self.addVoxels()

        # Update Camera Matrix
        self.matrices.V = self.camera.Compute()

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
        M = self.matrices
        # Render Opaque first

        self.cube.render(M)

        # Render origin when navigating
        if self.move_active:
            with M.Push(glm.translate(self.camera.center)):
                self.origin.render(M)

        # Render Bone Mesh
        if self.show_bone:
            with M.Push(self.t_bone):
                self.bone.render(M)

        # Render Normalized geometry
        with M.Push(self.t_norm):

            # Render Truss mesh
            if hasattr(self, 'truss'):
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
    from source.debug.performance import performance, GPU

    @window.keys.action("P")
    def perf():
        performance(GPU.NVIDIA)

    window.spin()
