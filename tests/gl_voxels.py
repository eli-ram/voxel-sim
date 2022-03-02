# pyright: reportUnusedImport=false, reportUnusedFunction=false
import __init__

# Interactive
from source.interactive.animator import Animator
from source.interactive.scene import SceneBase, Scene, Transform, Void
from source.interactive.window import Window
from source.interactive.tasks import FunctionalTask

# Other
from source.utils.wireframe.deformation import DeformationWireframe
from source.utils.wireframe.wireframe import Wireframe
from source.utils.mesh.simplemesh import Geometry, SimpleMesh
from source.utils.mesh.shapes import line_cube, origin, simplex
from source.math.truss2stress import fem_simulate
from source.math.voxels2truss import voxels2truss
from source.utils.mesh_loader import loadMeshes
from source.utils.directory import cwd, script_dir
from source.utils.matrices import OrbitCamera
from source.voxels.proxy import VoxelProxy
from source.utils.types import Array, F
from source.data.colors import Colors
from source.data.truss import Truss
from source.debug.time import time
from OpenGL.GL import *
from typing import Tuple
import numpy as np
import glm


@cwd(script_dir(__file__), '..', 'meshes')
@time("BONE")
def bone():
    BONE, = loadMeshes('test_bone.obj')
    return BONE


def mesh(get_bone: bool):
    if get_bone:
        # Load Bone Model
        s_mesh = bone()
        t_mesh = (
            glm.translate(glm.vec3(0.5, 0.5, -1.8)) *
            glm.scale(glm.vec3(0.5)) *
            glm.translate(glm.vec3(0, 0, -0.01)) *
            glm.rotate(glm.pi() / 2, glm.vec3(1, 0, 0))
        )

    else:
        # Load Simplex Model
        s_mesh = simplex()
        t_mesh = (
            glm.translate(glm.vec3(0.1, 0.1, 0.2)) *
            glm.scale(glm.vec3(0.9)) *
            glm.rotate(glm.radians(10.0), glm.vec3(0, 0, 1))
        )

    return s_mesh, t_mesh


def time_to_t(time: float, duration: float, padding: float):
    MOD = duration + 2 * padding
    D = (time % MOD) / duration
    T = max(min(D, 1.0), 0.0)
    return T


class Voxels(Window):

    BONE = False
    truss: DeformationWireframe

    def setup(self):
        self.scene = SceneBase((0.3, 0.2, 0.5))
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

        # Outline for Voxels
        self.scene.add(Wireframe(line_cube(), glm.vec4(0, 0, 0, 1), 1.0))

        # 3D-crosshair for camera
        self.move_cross = Transform(
            transform=glm.mat4(),
            mesh=Wireframe(origin(0.05), glm.vec4(1, 0.5, 0, 1), 1.0),
            hidden=True,
        )
        self.scene.add(self.move_cross)

        self.mesh, matrix = mesh(self.BONE)

        self.model = Transform(
            transform=matrix,
            mesh=Wireframe(self.mesh, glm.vec4(0.8, 0.8, 1, 1), 2.0),
        )
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
            self.move_active = move

        # Bind alpha controls
        K.action("U")(lambda: self.alpha(True))
        K.action("I")(lambda: self.alpha(False))

        # Bind toggle outline
        K.action("O")(self.voxels.toggle_outline)

        # Bind animator recording
        K.toggle("SPACE")(self.animator.record)

        self.tasks.sequence(
            self.makeVoxels(),
            self.makeStatic(),
            self.makeForce(),
            self.makeTruss(),
        )

    def alpha(self, up: bool):
        step = 1 if up else -1
        self.alphas: 'Array[F]' = np.roll(self.alphas, step)  # type: ignore
        self.voxels.set_alpha(self.alphas[0])

    def makeStatic(self):
        strength = np.ones((32, 32, 1), np.float32) * 8.0
        strength[5:27, 5:27, 0] = 0.0
        offset = (0, 0, 5)
        self.voxels.set_static("blue", (True, True, True))
        return self.voxels.add_box(offset, strength, "blue")

    def makeForce(self):
        strength = np.ones((5, 5, 1), np.float32) * 8.0
        offset = (9, 13, 15)
        self.voxels.set_force("red", (0, 0, -100))
        return self.voxels.add_box(offset, strength, "red")

    def makeTruss(self):

        # Move into Proxy

        def build():
            print("Building Truss")
            truss = voxels2truss(self.voxels.data)
            print("Simulating Truss")
            D, _ = fem_simulate(truss, 1E3)
            print("Creating Mesh")
            # Render mesh even if simulation failed
            if np.isnan(D).any():
                print("Fem simulation failed & produced nan")
                np.nan_to_num(D, copy=False)

            return truss, D

        def resolve(bundle: 'Tuple[Truss, Array[F]]'):
            print("Creating Deformation")
            truss, D = bundle
            color = glm.vec4(0.8, 0.8, 1, 1)
            M = SimpleMesh(truss.nodes, truss.edges, Geometry.Lines)
            self.truss = DeformationWireframe(M, D, color, 2.0)
            self.box.children[0] = self.truss
            print("Truss deformation created")

        return FunctionalTask(build, resolve)

    def makeVoxels(self):
        box = self.box.transform
        model = self.model.transform
        transform = glm.affineInverse(box) * model
        return self.voxels.add_mesh(self.mesh, transform, 0.5, "gray")

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
        if self.move_active:
            self.camera.Cursor(dx, dy)

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
