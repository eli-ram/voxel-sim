# pyright: reportUnusedImport=false, reportUnusedFunction=false
import __init__

# Packages
import glm
import numpy as np
from OpenGL.GL import *

# Data
from source.data.colors import Color, get
from source.data.mesh import Mesh

# Debug
from source.debug.time import time
from source.graphics import matrices as m

# Interactive
from source.interactive.animator import Animator
from source.interactive.scene import Scene, SceneBase, Transform, Void
from source.interactive.window import Window

# Utils
from source.utils import (
    directory as d,
    mesh_loader as l,
    shapes as s,
)
from source.utils.wireframe.deformation import DeformationWireframe
from source.utils.wireframe.wireframe import Wireframe

# Voxels
from source.voxels.proxy import VoxelProxy



def time_to_t(time: float, duration: float, padding: float):
    MOD = duration + 2 * padding
    D = (time % MOD) / duration
    T = max(min(D, 1.0), 0.0)
    return T


class Voxels(Window):

    BONE = False
    mesh: Mesh
    model: Transform
    truss: DeformationWireframe

    def setup(self):
        self.scene = SceneBase()
        self.scene.setBackground(Color(0.3, 0.2, 0.5))
        self.camera = m.OrbitCamera(
            distance=1.25,
            svivel_speed=0.005,
        )
        shape = (32, 32, 32)
        resolution = 2**10
        self.voxels = VoxelProxy(shape, resolution)
        self.voxels.createMaterials({
            "STATIC": get.BLUE,
            "FORCE": get.RED,
            "BONE": Color(0.3, 0.5, 0.3, 0.1),
        })

        # Store animator
        self.animator = Animator('animation.gif', delta=0.5)

        # Outline for Voxels
        self.scene.add(Wireframe(s.line_cube()).setColor(get.BLACK))

        # 3D-crosshair for camera
        self.move_cross = Transform(
            transform=glm.scale(glm.vec3(0.05, 0.05, 0.05)),
            mesh=Wireframe(s.origin_marker()).setColor(Color(1, 0.5, 0)),
            hidden=True,
        )
        self.scene.add(self.move_cross)

        self.model = Transform(None, None, hidden=True)  # type: ignore

        self.scene.add(self.model)

        # Normalze Voxel grid (0 -> N) => (0.0 -> 1.0)
        self.box = Scene(
            transform=glm.scale(glm.vec3(1/max(*shape))),
            children=[Void(), self.voxels.graphics]
        )
        self.scene.add(self.box)

        # Some internal state
        self.alphas = np.power(np.linspace(1.0, 0.0, 6), 2)  # type: ignore
        self.move_active = False

        # Getting Vars
        K = self.keys
        B = self.buttons

        # Toggle Bone
        K.action("H")(self.model.toggle)

        # Bind camera controls
        K.toggle("LEFT_CONTROL")(self.camera.SetPan)

        @B.toggle("LEFT")
        def toggle_move(move: bool):
            self.move_cross.visible(move)
            self.camera.SetActive(move)

        # Bind alpha controls
        K.action("U")(lambda: self.alpha(True))
        K.action("I")(lambda: self.alpha(False))

        # Bind toggle outline
        K.action("O")(self.voxels.toggle_outline)

        # Bind animator recording
        K.toggle("SPACE")(self.animator.record)

        self.build()

    def alpha(self, up: bool):
        step = 1 if up else -1
        self.alphas: 'Array[F]' = np.roll(self.alphas, step)  # type: ignore
        self.voxels.set_alpha(self.alphas[0])

    def build(self):
        if self.BONE:
            @d.cwd(d.script_dir(__file__), '..', 'meshes')
            @time("mesh")
            def compute():
                # Load Bone Model
                return l.loadMesh('test_bone.obj')

            self.model.transform = (
                glm.translate(glm.vec3(0.5, 0.5, -1.8)) *
                glm.scale(glm.vec3(0.5)) *
                glm.translate(glm.vec3(0, 0, -0.01)) *
                glm.rotate(glm.pi() / 2, glm.vec3(1, 0, 0))
            )

        else:
            def compute():
                # Load Simplex Model
                return s.simplex()

            self.model.transform = (
                glm.translate(glm.vec3(0.1, 0.1, 0.2)) *
                glm.scale(glm.vec3(0.9)) *
                glm.rotate(glm.radians(10.0), glm.vec3(0, 0, 1))
            )

        def complete(mesh: Mesh):
            self.mesh = mesh
            self.model.mesh = Wireframe(mesh)\
                .setColor(Color(0.8, 0.8, 1.0))
            self.model.hidden = False
            # Build the rest
            self.tasks.sequence(
                self.makeVoxels(),
                self.makeStatic(),
                self.makeForce(),
                self.makeTruss(),
            )

        self.tasks.run(compute, complete)

    def makeStatic(self):
        strength = np.ones((32, 32, 1), np.float32) * 8.0
        strength[5:27, 5:27, 0] = 0.0
        offset = (0, 0, 5)
        self.voxels.set_static("STATIC", (True, True, True))
        return self.voxels.add_box(offset, strength, "STATIC")

    def makeForce(self):
        strength = np.ones((5, 5, 1), np.float32) * 8.0
        offset = (9, 13, 15)
        self.voxels.set_force("FORCE", (0, 0, -100))
        return self.voxels.add_box(offset, strength, "FORCE")

    def makeTruss(self):
        @self.voxels.fem_simulate
        def task(truss: DeformationWireframe):
            self.truss = truss
            self.box.children[0] = truss
        return task

    def makeVoxels(self):
        box = self.box.transform
        model = self.model.transform
        transform = glm.affineInverse(box) * model
        return self.voxels.add_mesh(self.mesh, transform, 0.5, "BONE")

    def resize(self, width: int, height: int):
        self.animator.resize(width, height)
        glViewport(0, 0, width, height)
        self.scene.stack.SetPerspective(
            fovy=glm.radians(45.0),
            aspect=(width / height),
            near=0.01,
            far=100.0,
        )

    def update(self, time: float, delta: float):
        # Let the animator control the time if it's recording
        time, delta = self.animator.update(time, delta)

        # Update Camera Matrix
        self.scene.stack.V = self.camera.Compute()
        self.move_cross.transform = glm.translate(self.camera.center)

        # Change deformation
        if hasattr(self, 'truss'):
            T = time_to_t(time, 30, 3)
            self.truss.deformation = T * 5.0

    def render(self):
        self.scene.render()

    def cursor(self, x: float, y: float, dx: float, dy: float):
        self.camera.Cursor(dx, dy)

    def scroll(self, value: float):
        self.camera.Zoom(value)


if __name__ == '__main__':
    size = 900
    window = Voxels(size, size, "voxels")
    from source.debug.performance import GPU, performance

    @window.keys.action("P")
    def perf():
        performance(GPU.NVIDIA)

    window.spin()
