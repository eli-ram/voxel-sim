# pyright: reportUnusedImport=false, reportUnusedFunction=false
import numpy as np
import __init__

# Packages
import glm
from OpenGL import GL

# Interactive
import source.interactive.window as w
import source.interactive.scene as s
import source.interactive.animator as a

# Graphics
import source.graphics.matrices as m
from source.utils.wireframe.origin import Origin

# Utils
from source.utils.directory import directory, require, script_dir

# Parse
from source.loader.configuration import Configuration
from source.parser.detector import ParsableDetector
from source.voxels.render import VoxelRenderer


class Voxels(w.Window):

    def setup(self):
        # Create scene
        self.scene = s.SceneBase()

        # Create animator
        self.animator = a.Animator(delta=0.5)

        # Create Camera
        self.camera = m.OrbitCamera(
            distance=1.25,
            svivel_speed=0.005,
        )

        # Create Camera Origin
        self.cursor_3d = s.Transform(
            transform=glm.scale(glm.vec3(2.0)),
            # mesh=Wireframe(origin_marker(0.5)).setColor(Color(1, 0.5, 0)),
            mesh=Origin(),
            hidden=True,
        )

        # Bind Key Controls
        K = self.keys
        K.toggle("LEFT_CONTROL")(self.camera.SetPan)
        K.action("O")(self.cursor_3d.toggle)
        K.toggle("SPACE")(self.animator.recorder(
            require(script_dir(__file__), '..', 'results'),
            'animation{:[%Y-%m-%d][%H-%M]}.gif'
        ))

        # Bind Mouse Controls
        B = self.buttons

        @B.toggle("LEFT")
        def toggle_move(move: bool):
            self.camera.SetActive(move)
            self.cursor_3d.visible(move)

        # Build scene
        self.scene.setChildren([self.cursor_3d])

    def processConfig(self, config: Configuration):
        """ Process config (called from parser thread) """

        print("Processing config ...")

        # hack to get render-scene as local
        R = self.scene

        # synchronized context to render scene
        @self.tasks.dispatch
        def render():
            nonlocal R

            # Set background
            self.scene.setBackground(config.getBackground())

            # Build scene
            R = config.getRender()

            # Append scene, include 3D cursor
            self.scene.setChildren([R, self.cursor_3d])

        # Compute voxels
        N = config.getVoxels()

        # Wait for render to finish
        render.wait()

        # Not configured for voxels
        if N is None:
            print("Did not build voxels")
            return

        # synchronized context to render voxels
        @self.tasks.dispatch
        def voxels():
            print("voxels:", N.data.box)
            # Build voxel renderer
            V, T = config.getVoxelRenderer(N.data) 
            # Transform renderer into the scene
            R.add(s.Transform(T, V))

        # Wait for voxels to finish
        voxels.wait()

    def resize(self, width: int, height: int):
        self.animator.resize(width, height)
        GL.glViewport(0, 0, width, height)
        self.scene.stack.SetPerspective(
            fovy=glm.radians(45.0),
            aspect=(width / height),
            near=0.001,
            far=1000.0,
        )

    def update(self, time: float, delta: float):
        # Let the animator control the time if it's recording
        time, delta = self.animator.update(time, delta)

        # Update Camera Matrix
        self.scene.setCamera(self.camera.Compute())
        self.cursor_3d.transform = glm.translate(self.camera.center)

    def render(self):
        self.scene.render()

    def cursor(self, x: float, y: float, dx: float, dy: float):
        self.camera.Cursor(dx, dy)

    def scroll(self, value: float):
        self.camera.Zoom(value)


if __name__ == '__main__':
    # Create Window
    window = Voxels(900, 900, "voxels")

    # Create Configuration
    @ParsableDetector[Configuration]
    def detector(config: Configuration):
        config.configure(window.tasks, window.scene)
        window.scene.add(window.cursor_3d)

    # Run Configuration thread
    with directory(script_dir(__file__), "..", "configurations"):
        detector("test_3.yaml")

    # Run window
    window.spin()
