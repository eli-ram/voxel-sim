# pyright: reportUnusedImport=false, reportUnusedFunction=false
from typing import TypeVar

# Packages
import glm
from OpenGL import GL

# Interactive
import source.interactive.window as w
import source.interactive.scene as s
import source.interactive.animator as an
import source.interactive.screencapture as sc

# Graphics
import source.graphics.matrices as m
from source.utils.wireframe.deformation import DeformationWireframe
from source.utils.wireframe.origin import Origin

# Utils
from source.utils.directory import directory, require, script_dir

# Parse
from source.loader.configuration import Configuration
from source.parser.detector import ParsableDetector

# ML
import source.ml.ga_2 as ga

# The Configuration file path
# CONF = "configurations/final/whole#1.yaml"
CONF = "configurations/final/whole#2.yaml"
# CONF = "configurations/final/sliced#1.yaml"
# CONF = "configurations/final/sliced#2.yaml"
# CONF = "configurations/final/preview.yaml"

WORKSPACE = require(script_dir(__file__), "..")
RESULTS_DIR = require(WORKSPACE, "results")


# TODO: make a proper headless mode
# there is no need to init OpenGL & open a window
ENB_HEADLESS = False


def any_fn(*_a, **_k):
    pass


F = TypeVar("F")


def headless(fn: F) -> F:
    if ENB_HEADLESS:
        return any_fn  # type: ignore
    return fn


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
    configuration: Configuration
    deformation: DeformationWireframe | None = None
    algorithm: ga.GA | None = None
    present: s.Scene

    @headless
    def setup(self):
        # Create scene
        self._scene = s.SceneBase()

        # Create animator
        self._animator = an.Animator(delta=0.25)

        # Create screencapure
        self._capture = sc.Screencapture()

        # Create Camera
        self._camera = m.OrbitCamera(
            distance=1.25,
            # svivel_speed=0.005,
            svivel_speed=glm.radians(0.5),
        )

        # Create Camera Origin
        self._cursor = s.Transform(
            transform=glm.scale(glm.vec3(2.0)),
            mesh=Origin(),
            hidden=True,
        )

        # Bind Key Controls
        K = self.keys
        K.toggle("LEFT_CONTROL")(self._camera.SetPan)
        K.action("O")(self._cursor.toggle)
        # Recording hook
        K.toggle("SPACE")(
            self._animator.recorder(
                require(RESULTS_DIR, "gifs"),
                "animation{:[%Y-%m-%d][%H-%M]}.gif",
            )
        )
        # Screenshot hook
        K.action("F12")(
            self._capture.screenshot(
                require(RESULTS_DIR, "images"),
                "capture{:[%Y-%m-%d][%H-%M-%S]}.png",
            )
        )

        # KeyPad Camera control
        C = self._camera
        K.action("KP_DECIMAL")(lambda: C.SetCenter(glm.vec3()))
        K.action("KP_0")(lambda: C.SetDistance(2.0))
        K.repeat("KP_8")(lambda: C.Svivel(0.0, +10.0))
        K.repeat("KP_2")(lambda: C.Svivel(0.0, -10.0))
        K.action("KP_5")(lambda: C.SetAngles(0.0, 0.0))
        K.repeat("KP_4")(lambda: C.Svivel(+10.0, 0.0))
        K.repeat("KP_6")(lambda: C.Svivel(-10.0, 0.0))
        K.action("KP_7")(lambda: C.SetAngles(45.0, 45.0 - 0.0))
        K.action("KP_9")(lambda: C.SetAngles(45.0, 45.0 + 90.0))
        K.action("KP_3")(lambda: C.SetAngles(45.0, 45.0 + 180.0))
        K.action("KP_1")(lambda: C.SetAngles(45.0, 45.0 - 90.0))

        # Bind Mouse Controls
        B = self.buttons

        @B.toggle("LEFT")
        def _toggle_move(enb: bool):
            self._camera.SetActive(enb)
            self._cursor.visible(enb)

        # Build scene
        self._scene.setChildren([self._cursor])

    @headless
    def resize(self, width: int, height: int):
        self._animator.resize(width, height)
        self._capture.resize(width, height)
        GL.glViewport(0, 0, width, height)
        self._scene.stack.SetPerspective(
            fovy=glm.radians(45.0),
            aspect=(width / height),
            near=0.001,
            far=1000.0,
        )

    @headless
    def update(self, time: float, delta: float):
        # Let the animator control the time if it's recording
        time, delta = self._animator.update(time, delta)

        # Update Camera Matrix
        self._scene.setCamera(self._camera.Compute())
        self._cursor.transform = glm.translate(self._camera.center)

        # Update deformation if set
        if D := self.deformation:
            t = time_to_t(time, 30.0, 2.5)
            D.setDeformation(t)

    @headless
    def render(self):
        self._scene.render()

    @headless
    def cursor(self, x, y, dx, dy):
        self._camera.Cursor(dx, dy)

    @headless
    def scroll(self, value: float):
        self._camera.Zoom(value)

    @headless
    def presentSolution(self, data):
        V = self.configuration.getVoxelRenderer(data)
        self.present.children[-1] = V

    def spinAlgorithm(self):
        A = self.algorithm

        # not allowed to run
        if A is None or A.running:
            return

        # try to run next step
        def resolve(data):
            # cancelled
            if data is None:
                return

            # Present solution
            self.presentSolution(data)

            # queue next iteration
            self.spinAlgorithm()

        # run a step of the algorithm
        self.tasks.run(A.step, resolve, "algorithm")

    def watch(self, config: str):
        # Create Configuration
        @ParsableDetector[Configuration]
        def cimpl(config: Configuration):
            TQ = self.tasks
            print("Processing config ...")
            self.configuration = config

            # bypass in headless mode
            if ENB_HEADLESS:
                # only compute voxels
                config.voxels()

            else:
                # Background
                BG = config.background()
                TQ.dispatch(lambda: self._scene.setBackground(BG))

                # Build scene
                S = config.scene(TQ)
                self._scene.setChildren([self._cursor, S])
                self.present = S

                # Configure
                config.configure(TQ, S)
                # Run more
                # self.deformation = config.run(TQ, S)

            # Get algorithm
            alg = config.buildAlgorithm(RESULTS_DIR)
            if alg is None:
                # no algorithm instance
                self.algorithm = None

            elif self.algorithm != alg:
                # new algorithm instance
                self.algorithm = alg
                self.spinAlgorithm()

            # Display current solution
            if alg and (data := alg.current()):
                TQ.dispatch(lambda: self.presentSolution(data))

        # run
        cimpl(config)


if __name__ == "__main__":
    # Create Window
    window = Voxels(900, 900, "voxels")

    # Run Configuration thread
    with directory(WORKSPACE):
        window.watch(CONF)

    # Run window
    window.spin()
