# pyright: reportUnknownArgumentType=false
from ctypes import c_void_p as ptr
from OpenGL.GL import *  # type: ignore
from OpenGL.GL.shaders import *  # type: ignore
from OpenGL.arrays.vbo import *  # type: ignore
import numpy as np

from .shaders.swarmshader import ComputeCache, RenderCache
from ..utils.types import int2
from ..utils.texture import Texture2D, TextureSet
from ..utils.directory import cwd, script_dir
from ..utils.framebuffer import Framebuffer



class Swarm:

    @cwd(script_dir(__file__), 'shaders')
    def __init__(self, shape: int2):
        self.compute = ComputeCache.get()
        self.render = RenderCache.get()
        self.textures = TextureSet(0, [
            Texture2D(shape),
            Texture2D(shape),
        ])
        self.framebuffer = Framebuffer()

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
        with self.agents, self.render as (A, _):
            stride = 4 * item
            glVertexAttribPointer(A.position, 2, GL_FLOAT, GL_FALSE, stride, ptr(0 * item))
            glVertexAttribPointer(A.direction, 1, GL_FLOAT, GL_FALSE, stride, ptr(2 * item))
            glVertexAttribPointer(A.velocity, 1, GL_FLOAT, GL_FALSE, stride, ptr(3 * item))

            # TODO: find right location
            glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, self.agents)

    def update(self, time: float, delta: float):

        with self.textures, self.compute as (_, U):
            glUniform1f(U.time, time)
            glDispatchCompute(self.count // 16, 1, 1)

        self.textures.swap(0, 1)

        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        with self.framebuffer, self.agents, self.render:
            self.framebuffer.output(self.textures[0])
            # self.framebuffer.check()
            glDrawArrays(GL_POINTS, 0, self.count)




