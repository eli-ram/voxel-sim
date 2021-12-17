# pyright: reportUnusedImport=false, reportUnusedFunction=false
import __init__
from source.interactive.Animator import Animator
from source.utils.wireframe.deformation import DeformationWireframe
from source.utils.wireframe.wireframe import Wireframe
from source.utils.mesh.simplemesh import Geometry, SimpleMesh
from source.utils.mesh.shapes import line_cube, origin, simplex
from source.math.truss2stress import fem_simulate
from source.math.voxels2truss import voxels2truss
from source.utils.mesh_loader import loadMeshes
from source.math.mesh2voxels import mesh_2_voxels, transform
from source.utils.directory import cwd, script_dir
from source.utils.matrices import Hierarchy, OrbitCamera
from source.voxels.proxy import VoxelProxy, remove_padding
from source.utils.types import Array, T
from source.data.colors import Colors
from source.interactive import Window, Animator
from source.debug.time import time
from source.utils.misc import random_box
from OpenGL.GL import *
from typing import Any
from random import choice
import numpy as np
import asyncio
import glm


@cwd(script_dir(__file__), '..', 'meshes')
@time("BONE")
def bone():
    BONE, = loadMeshes('test_bone.obj')
    return BONE


def time_to_t(time: float, duration: float, padding: float):
    MOD = duration + 2 * padding
    D = (time % MOD) / duration
    T = max(min(D, 1.0), 0.0)
    return T


class Voxels(Window):

    def setup(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.4, 0.4, 0.8, 1.0)
        self.matrices = Hierarchy()
        self.camera = OrbitCamera(
            distance=1.25,
            svivel_speed=0.005,
        )
        shape = (32, 32, 32)
        resolution = 2**10
        self.voxels = VoxelProxy(shape, resolution, {
            "blue": Colors.BLUE,
            "green": Colors.GREEN,
            "red": Colors.RED,
            "gray": Colors.GRAY,
        })

        # Store animator
        self.animator = Animator('animation.gif', delta=0.5)

        # Get list of materials
        self.materials = self.voxels.material_list()

        # 3D-crosshair for camera
        self.origin = Wireframe(origin(0.05), glm.vec4(1, 0.5, 0, 1), 1.0)

        # Outline for Voxels
        self.cube = Wireframe(line_cube(), glm.vec4(0, 0, 0, 1), 1.0)

        # Bone Model
        # TODO: async load
        # self.bone_mesh = bone()
        self.bone_mesh = simplex()
        self.bone = Wireframe(
            self.bone_mesh,
            glm.vec4(0.8, 0.8, 1, 1),
            2.0,
        )

        # self.deformation = test_case()

        # Cache transforms

        # Normalze Voxel grid (0 -> N) => (0.0 -> 1.0)
        self.t_norm = glm.scale(glm.vec3(1/max(*shape)))
        """
        self.t_bone = (
            glm.translate(glm.vec3(0.5, 0.5, -1.8)) *
            glm.scale(glm.vec3(0.5)) *
            glm.translate(glm.vec3(0, 0, -0.01)) *
            glm.rotate(glm.pi() / 2, glm.vec3(1, 0, 0))
        )
        """
        self.t_bone = (
            glm.translate(glm.vec3(0.1, 0.1, 0.2)) *
            glm.scale(glm.vec3(0.9)) *
            glm.rotate(glm.radians(10.0), glm.vec3(0, 0, 1))
        )

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
        @K.action("H")
        def show():
            self.show_bone = not self.show_bone

        # Bind camera controls
        @K.toggle("LEFT_CONTROL")
        def mode(m: bool):
            self.move_mode = m

        @B.toggle("LEFT")
        def active(a: bool):
            self.move_active = a

        # Bind alpha controls
        K.action("U")(lambda: self.alpha(True))
        K.action("I")(lambda: self.alpha(False))

        # Bind toggle outline
        K.action("O")(self.voxels.toggle_outline)

        # Bind other controls
        K.action("R")(lambda: T.run(self.wireframe()))
        K.action("B")(lambda: T.run(self.get_bone_voxels()))

        # Bind animator recording
        K.toggle("SPACE")(self.animator.record)

        self.add_other()

        async def ticks():
            b = False
            while True:
                print("tick" if (b := not b) else "tock")
                await asyncio.sleep(10)

        T.run(ticks())

    def alpha(self, up: bool):
        step = 1 if up else -1
        self.alphas: 'np.ndarray[np.float32]' = \
            np.roll(self.alphas, step)  # type: ignore
        self.voxels.set_alpha(self.alphas[0])

    def add_other(self):
        strength = np.ones((32, 32, 1), np.float32) * 8.0
        strength[5:27, 5:27, 0] = 0.0
        offset = (0, 0, 5)
        self.voxels.set_static("blue", (True, True, True))
        self.voxels.add_box(offset, strength, "blue")

        strength = np.ones((5, 5, 1), np.float32) * 8.0
        offset = (9, 13, 15)
        self.voxels.set_force("red", (0, 0, -100))
        self.voxels.add_box(offset, strength, "red")

    async def wireframe(self):
        color = glm.vec4(0.8, 0.8, 1, 1)
        print("Building Truss")
        truss = await self.tasks.parallel(voxels2truss, self.voxels.data)
        print("Simulating Truss")
        DandE = self.tasks.parallel(fem_simulate, truss, 1E3)
        print("Creating Mesh")
        M = SimpleMesh(truss.nodes, truss.edges, Geometry.Lines)
        D, _ = await DandE
        # Render mesh even if simulation failed
        np.nan_to_num(D, copy=False)
        print("Creating Deformation")
        self.truss = DeformationWireframe(M, D, color, 2.0)
        print("Truss deformation created")

    async def get_bone_voxels(self):
        print("get-bone-voxels")
        import numpy as np
        t = glm.affineInverse(self.t_norm) * self.t_bone
        t = self.matrices.copy(t)[:3, :]
        T = self.tasks
        S = self.voxels.data.shape
        V, I = await T.parallel(transform, self.bone_mesh, t)

        def grid(D: str):
            G = mesh_2_voxels(V, I, S, D)
            return G.astype(np.float32)

        X = T.parallel(grid, "X")
        Y = T.parallel(grid, "Y")
        Z = T.parallel(grid, "Z")

        def combine(X: 'Array[T]', Y: 'Array[T]', Z: 'Array[T]'):
            G = X + Y + Z
            S = np.float32(0.5)
            O = np.float32(0.0)
            # Patch out errors by requiring best of 3
            strength = np.where(G > 1.0, S, O)  # type: ignore
            # Reduce later operation complexity
            return remove_padding(strength)

        offset, strength = await T.parallel(combine, await X, await Y, await Z)
        self.voxels.add_box(offset, strength, "gray")
        self.add_other()

    def resize(self, width: int, height: int):
        self.animator.resize(width, height)
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
        # Let the animator control the time if it's recording
        time, delta = self.animator.update(time, delta)

        # Update Camera Matrix
        self.matrices.V = self.camera.Compute()

        # Change deformation
        if hasattr(self, 'truss'):
            T = time_to_t(time, 30, 3)
            self.truss.deformation = T * 5.0

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
            self.voxels.graphics.render(M)

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
