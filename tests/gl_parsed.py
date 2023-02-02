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
    MOD = duration + 2 * padding
    D = (time % MOD - padding) / duration
    T = max(min(D, 1.0), 0.0)
    return T


class Voxels(w.Window):

    deformation: Optional[DeformationWireframe] = None

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
        def toggle_move(move: bool):
            self.camera.SetActive(move)
            self._3D_cursor.visible(move)

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
            t = time_to_t(time, 30.0, 5.0)
            D.setDeformation(t)

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
        # Attrs
        TQ = window.tasks
        S = window.scene
        # Configure
        R, BG = config.configure(TQ)
        # Set scene
        TQ.dispatch(lambda: S.setBackground(BG))
        S.setChildren([window._3D_cursor, R])
        # Run more
        D = config.run(TQ)
        # deformation mesh attatchment
        # window.deformation = D

    # Run Configuration thread
    with directory(script_dir(__file__), "..", "configurations"):
        detector("test_4.yaml")

    # Run window
    window.spin()
