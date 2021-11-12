# pyright: reportUnknownArgumentType=false
from ctypes import c_void_p as ptr
from source.utils.texture import Size_2D, Texture2D, TextureSet
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import *  # type: ignore
from OpenGL.arrays.vbo import *  # type: ignore
import numpy as np

from ..utils import (
    shader, cwd, script_dir,
    Framebuffer, ShaderUniforms, ShaderAttributes,
)


class RenderAttributes(ShaderAttributes):
    position: int
    velocity: int
    direction: int

class RenderUniforms(ShaderUniforms):
    pass

class ComputeAttributes(ShaderAttributes):
    Source: int
    agents: int

class ComputeUniforms(ShaderUniforms):
    environment: int
    time: int

class Swarm:

    @cwd(script_dir(__file__), 'shaders')
    def __init__(self, shape: Size_2D):
        self.compute = shader('swarm.comp')
        self.render = shader('swarm.vert', 'swarm.geom', 'swarm.frag')
        self.textures = TextureSet(0, [
            Texture2D(shape),
            Texture2D(shape),
        ])
        self.framebuffer = Framebuffer()

        self.render_attrs = RenderAttributes(self.render)()
        self.compute_attr = ComputeAttributes(self.compute)()
        self.compute_unif = ComputeUniforms(self.compute)()

    def set_size(self, size: int):
        # Prefer Multiples of 16 !
        size = (size // 16) * 16
        rng = np.random.default_rng()

        data = np.zeros((size, 4), dtype=np.float32)
        data[:, 0] = rng.uniform(-1.0, 1.0, size)
        data[:, 1] = rng.uniform(-1.0, 1.0, size)
        data[:, 2] = np.arctan2(data[:,0], data[:,1]) + np.pi / 2 # type: ignore
        data[:, 3] = rng.choice([0.001, 0.002], size) # type: ignore
        
        self.agents = VBO(data, target=GL_ARRAY_BUFFER)
        self.count = size

        glLineWidth(1.0)

        item = data.itemsize
        attr = self.render_attrs
        with self.agents:
            stride = 4 * item
            glVertexAttribPointer(attr.position, 2, GL_FLOAT, GL_FALSE, stride, ptr(0 * item))
            glVertexAttribPointer(attr.direction, 1, GL_FLOAT, GL_FALSE, stride, ptr(2 * item))
            glVertexAttribPointer(attr.velocity, 1, GL_FLOAT, GL_FALSE, stride, ptr(3 * item))

            # TODO: find right location
            glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.agents)

    def update(self, time: float, delta: float):

        with self.compute, self.textures:
            glUniform1f(self.compute_unif.time, time)
            glDispatchCompute(self.count // 16, 1, 1)

        self.textures.swap(0, 1)

        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        with self.framebuffer, self.render, self.agents, self.render_attrs:
            self.framebuffer.output(self.textures[0])
            # self.framebuffer.check()
            glDrawArrays(GL_POINTS, 0, self.count)




