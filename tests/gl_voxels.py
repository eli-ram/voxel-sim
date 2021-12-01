# pyright: reportUnusedImport=false, reportUnusedFunction=false
import asyncio
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
from source.math.mesh2voxels import mesh_2_voxels, transform
from source.voxels.proxy import VoxelProxy
from OpenGL.GL import *
from random import random, choice


"""
TODO:

- Stiffness Matrix
    https://www.youtube.com/watch?v=3uzf_938V4c

        > T = Local To Global
        > T.T = Global To Local
        > C = Connectivity
        > Strength = Area * Elasticity / Length
        > Stiffness = Strengh * T.T * C * T
        # linear system
        > F = Stiffness * V 

- Imitate Matlab Behavoiur 
    https://se.mathworks.com/matlabcentral/answers/348024-summing-values-for-duplicate-rows-and-columns
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
        shape = (512, 512, 512)
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
            glm.translate(glm.vec3(0.5, 0.5, -1.8)) *
            glm.scale(glm.vec3(0.5)) *
            glm.translate(glm.vec3(0, 0, -0.01)) *
            glm.rotate(glm.pi() / 2, glm.vec3(1, 0, 0))
        )
        """
        self.t_bone = (
            glm.translate(glm.vec3(0.2)) *
            glm.scale(glm.vec3(0.8))
        )
        """

        # Some internal state
        self.alphas = np.power(np.linspace(1.0, 0.0, 6), 3)  # type: ignore
        self.move_mode = False
        self.move_active = False
        self.show_bone = True

        # Getting Vars
        K = self.keys
        B = self.buttons
        T = self.tasks

        # Toggle Bone
        K.action("H")(lambda: setattr(self, 'show_bone', not self.show_bone))

        # Bind camera controls
        K.toggle("LEFT_CONTROL")(
            lambda press: setattr(self, 'move_mode', press))
        B.toggle("LEFT")(lambda press: setattr(self, 'move_active', press))

        # Bind alpha controls
        K.action("U")(lambda: self.alpha(True))
        K.action("I")(lambda: self.alpha(False))

        # Bind toggle outline
        K.action("O")(self.voxels.toggle_outline)

        # Bind other controls
        K.action("R")(lambda: T.run(self.wireframe()))
        K.action("B")(lambda: T.run(self.get_bone_voxels()))

    def alpha(self, up: bool):
        step = 1 if up else -1
        self.alphas: 'np.ndarray[np.float32]' = \
            np.roll(self.alphas, step)  # type: ignore
        self.voxels.set_alpha(self.alphas[0])

    async def wireframe(self):
        color = glm.vec4(0.8, 0.8, 1, 1)
        self.truss = await self.tasks.parallel(self.voxels.get_mesh, color)

    async def get_bone_voxels(self):
        print("get-bone-voxels")
        import numpy as np
        t = glm.affineInverse(self.t_norm) * self.t_bone
        t = self.matrices.ptr(t)[:3, :]
        T = self.tasks
        S = self.voxels.data.shape
        V, I = await T.parallel(transform, self.bone_mesh, np.copy(t))

        async def grid(D: str, M: str):
            print("Computing", D, '->', M)
            G = await T.parallel(mesh_2_voxels, V, I, S, D)
            print("Rendering", D , '->', M)
            self.voxels.add_box((0, 0, 0), G.astype(np.float32), M)
            print("Finished", D, '->', M)
            return G

        gx = await grid("X", "red")
        gy = await grid("Y", "blue")
        gz = await grid("Z", "green")

        print("Adding gray inners")
        g = gx & gy & gz
        self.voxels.add_box((0, 0, 0), g.astype(np.float32), "gray")

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

    window.start()
