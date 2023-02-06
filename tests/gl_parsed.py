# pyright: reportUnusedImport=false, reportUnusedFunction=false
from typing import Optional
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
from source.utils.wireframe.deformation import DeformationWireframe
from source.utils.wireframe.origin import Origin

# Utils
from source.utils.directory import directory, require, script_dir

# Parse
from source.loader.configuration import Configuration
from source.parser.detector import ParsableDetector


def time_to_t(time: float, duration: float, padding: float):
    M = time % (duration + padding + padding)
    D = (M - padding) / duration
    # Wait
    if D < 0.0:
        return 0.0
    # Stall
    if D > 1.0:
        return 1.0
    # Interpolate
    return D


class Voxels(w.Window):

    deformation: Optional[DeformationWireframe] = None

    def setup(self):
        # Create scene
        self.scene = s.SceneBase()

        # Create animator
        self.animator = a.Animator(delta=0.25)

        # Create Camera
        self.camera = m.OrbitCamera(
            distance=1.25,
            svivel_speed=0.005,
        )

        # Create Camera Origin
        self._3D_cursor = s.Transform(
            transform=glm.scale(glm.vec3(2.0)),
            mesh=Origin(),
            hidden=True,
        )

        # Bind Key Controls
        K = self.keys
        K.toggle("LEFT_CONTROL")(self.camera.SetPan)
        K.action("O")(self._3D_cursor.toggle)
        K.toggle("SPACE")(self.animator.recorder(
            require(script_dir(__file__), '..', 'results'),
            'animation{:[%Y-%m-%d][%H-%M]}.gif'
        ))

        # Bind Mouse Controls
        B = self.buttons

        @B.toggle("LEFT")
        def toggle_move(enb: bool):
            self.camera.SetActive(enb)
            self._3D_cursor.visible(enb)

        # Build scene
        self.scene.setChildren([self._3D_cursor])

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
        self._3D_cursor.transform = glm.translate(self.camera.center)

        # Update deformation if set
        if D := self.deformation:
            t = time_to_t(time, 30.0, 2.5)
            D.setDeformation(t)

    def render(self):
        self.scene.render()

    def cursor(self, x: float, y: float, dx: float, dy: float):
        self.camera.Cursor(dx, dy)

    def scroll(self, value: float):
        self.camera.Zoom(value)

    def detector(self, config: str):
        # Create Configuration
        @ParsableDetector[Configuration] 
        def impl(config: Configuration):
            TQ = self.tasks
            print("Processing config ...")

            # Background
            BG = config.background()
            TQ.dispatch(lambda: self.scene.setBackground(BG))

            # Build scene
            S = config.scene(TQ)
            self.scene.setChildren([self._3D_cursor, S])

            # Configure
            config.configure(TQ, S)
            # Run more
            D = config.run(TQ, S)
            # deformation mesh attatchment
            window.deformation = D

        # run
        impl(config) 


if __name__ == '__main__':
    # Create Window
    window = Voxels(900, 900, "voxels")

    # Run Configuration thread
    with directory(script_dir(__file__), "..", "configurations"):
        window.detector("test_4.yaml")

    # Run window
    window.spin()
