# pyright: reportUnusedImport=false, reportUnusedFunction=false
import __init__

# Packages
import glm
from OpenGL.GL import *

# Interactive
from source.interactive import (
    animator,
    window as w,
    scene as s,
)

# Graphics
from source.graphics import matrices as m
from source.utils.wireframe.origin import Origin

# Utils
from source.utils.wireframe.wireframe import Wireframe
from source.utils.directory import directory, require, script_dir
from source.utils.shapes import origin_marker

# Data
from source.data.colors import Color

# Parse
from source.loader.configuration import Configuration
from source.loader.parse.detector import ParsableDetector


class Voxels(w.Window):

    def setup(self):
        # Create scene
        self.scene = s.SceneBase()

        # Create animator
        self.animator = animator.Animator(delta=0.5)

        # Create Camera
        self.camera = m.OrbitCamera(
            distance=1.25,
            svivel_speed=0.005,
        )

        # Create Camera Origin
        self.origin = s.Transform(
            transform=glm.mat4(),
            # mesh=Wireframe(origin_marker(0.5)).setColor(Color(1, 0.5, 0)),
            mesh=Origin(),
            hidden=True,
        )

        # Bind Key Controls
        K = self.keys
        K.toggle("LEFT_CONTROL")(self.camera.SetPan)
        K.action("O")(self.origin.toggle)
        K.toggle("SPACE")(self.animator.recorder(
            require(script_dir(__file__), '..', 'results'),
            'animation{:[%Y-%m-%d][%H-%M]}.gif'
        ))

        # Bind Mouse Controls
        B = self.buttons
        B.toggle("LEFT")(self.camera.SetActive)

        # Build scene
        self.scene.setChildren([self.origin])

    def processConfig(self, config: Configuration):

        # Use Config In synchronized context
        def synchronized(config: Configuration):
            self.scene.setBackground(
                config.getBackground()
            )

            self.scene.setChildren([
                config.getRender(),
                self.origin,
            ])

        self.tasks.sync(config, synchronized)

    def resize(self, width: int, height: int):
        self.animator.resize(width, height)
        glViewport(0, 0, width, height)
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
        self.origin.transform = glm.translate(self.camera.center)

    def render(self):
        self.scene.render()

    def cursor(self, x: float, y: float, dx: float, dy: float):
        self.camera.Cursor(dx, dy)

    def scroll(self, value: float):
        self.camera.Zoom(value)


if __name__ == '__main__':
    window = Voxels(900, 900, "voxels")
    detector = ParsableDetector[Configuration](window.processConfig)
    with directory(script_dir(__file__), "..", "configurations"):
        detector("test_2.yaml")
    window.spin()
