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

# Utils
from source.utils.wireframe.wireframe import Wireframe
from source.utils.directory import directory, script_dir
from source.utils.shapes import origin_marker

# Data
from source.data.colors import Color

# Parse
from source.loader.configuration import Configuration
from source.loader.parse.detector import ParsableDetector

class Voxels(w.Window):

    def setup(self):
        # Create animator
        self.animator = animator.Animator('animation.gif', delta=0.5)

        # Create Camera
        self.camera = m.OrbitCamera(
            distance=1.25,
            svivel_speed=0.005,
        )

        # Create Camera Origin
        self.origin = s.Transform(
            transform=glm.scale(glm.vec3(0.05, 0.05, 0.05)),
            mesh=Wireframe(origin_marker()).setColor(Color(1, 0.5, 0)),
            hidden=True,
        )

        # Bind Key Controls
        K = self.keys
        K.toggle("LEFT_CONTROL")(self.camera.SetPan)
        K.toggle("SPACE")(self.animator.record)
        K.action("O")(self.origin.toggle)

        # Bind Mouse Controls
        B = self.buttons
        B.toggle("LEFT")(self.camera.SetActive)

        # Build scene
        self.buildScene()

    def processConfig(self, config: Configuration):

        # Use Config In synchronized context
        def synchronized(config: Configuration):
            self.buildScene(config.getRender())

        self.tasks.sync(config, synchronized)

    def buildScene(self, *extra: s.Render):
        self.scene = s.SceneBase((0.3, 0.2, 0.5))
        self.scene.add(self.origin)
        for render in extra:
            self.scene.add(render)

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