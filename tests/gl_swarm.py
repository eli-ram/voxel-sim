import __init__
import numpy as np
from source.interactive.window import Window
from source.swarm.shaders import RectCache
from source.utils.animated import Animated
from source.swarm import Swarm
from OpenGL.GL import *

SIZE = (1500 // 16) * 16

class Swarm_Window(Window):

    def setup(self):
        # glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        self.swarm = Swarm((SIZE, SIZE))
        self.swarm.set_size(10_000)
        self.rect = RectCache.get()
        self.square = np.array([  # type: ignore
            [-1, -1],
            [+1, -1],
            [+1, +1],
            [-1, +1],
        ], np.float32)

        def diff(value: float):
            with self.swarm.fade as (_, U):
                glUniform1f(U.diff, value)
        self.diff = Animated(diff, 0.502, 0.001)

        def decay(value: float):
            with self.swarm.fade as (_, U):
                glUniform1f(U.decay, value)
        self.decay = Animated(decay, 0.801, 0.001)

        self.set_position(500, 10)

    def resize(self, width: int, height: int):
        glViewport(0, 0, width, height)
        if width > height:
            a = (height / width), 1.0
        else:
            a = 1.0, (width / height)
        with self.rect as (_, U):
            glUniform2f(U.aspect, *a)
        with self.swarm.render as (_, R):
            glUniform2f(R.aspect, *a)

    def update(self, time: float, delta: float):
        for _ in range(4):
            self.swarm.update(time, delta)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
        glEnableClientState(GL_VERTEX_ARRAY)
        with self.rect, self.swarm.textures:
            glVertexPointer(2, GL_FLOAT, 0, self.square)
            glDrawArrays(GL_QUADS, 0, 4)


if __name__ == '__main__':
    print("initializing ...")
    window = Swarm_Window(SIZE, SIZE, "Swarm")

    @window.keys.action("1")
    def inc_diff():
        window.diff.inc()

    @window.keys.action("2")
    def dec_diff():
        window.diff.dec()

    @window.keys.action("3")
    def inc_decay():
        window.decay.inc()

    @window.keys.action("4")
    def dec_decay():
        window.decay.dec()

    window.spin()

