import __init__
import numpy as np
from source.interactive import Window
from source.utils import shader, cwd, ShaderUniforms, Animated, bind
from source.swarm import Swarm
from OpenGL.GL import *

SIZE = (1000 // 16) * 16

class FadeUniforms(ShaderUniforms):
    diff: int
    decay: int

class RectUniforms(ShaderUniforms):
    aspect: int

class Swarm_Window(Window):

    @cwd('../shaders')
    def setup(self):
        # glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        self.swarm = Swarm((SIZE, SIZE))
        self.swarm.set_size(1_000_000)
        self.fade = shader('fade.comp')
        self.shader = shader('rect.frag', 'rect.vert')
        self.square = np.array([ # type: ignore
            [-1, -1],
            [+1, -1],
            [+1, +1],
            [-1, +1],
        ], np.float32)

        # conf smooth shader
        self.u_fade = FadeUniforms(self.fade)()

        @bind(self.fade)
        def diff(value: float):
            glUniform1f(self.u_fade.diff, value)
        self.diff = Animated(diff, 0.505, 0.001)

        @bind(self.fade)
        def decay(value: float):
            glUniform1f(self.u_fade.decay, value)
        self.decay = Animated(decay, 0.801, 0.001)

        # conf render shader
        self.u_shader = RectUniforms(self.shader)()

        self.set_position(500, 10)

    def resize(self, width: int, height: int):
        glViewport(0, 0, width, height)
        if width > height:
            aspect = [(height / width), 1.0] 
        else:
            aspect = [1.0, (width / height)]
        with self.shader:
            glUniform2f(self.u_shader.aspect, *aspect)

    def update(self, time: float, delta: float):
        with self.fade, self.swarm.textures:
            glDispatchCompute(SIZE//16, SIZE//16, 1)

        self.swarm.update(time, delta)

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore
        glEnableClientState(GL_VERTEX_ARRAY)
        with self.shader, self.swarm.textures:
            glVertexPointer(2, GL_FLOAT, 0, self.square)
            glDrawArrays(GL_QUADS, 0, 4)


if __name__ == '__main__':
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
