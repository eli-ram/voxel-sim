from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
from dataclasses import dataclass
from ..utils.shaders import (
    ShaderAttributes,
    ShaderUniforms,
    ShaderCache,
)
from ..utils.directory import cwd, script_dir
from ..utils.matrices import Hierarchy

from ctypes import c_void_p as ptr
import numpy as np
import glm


@dataclass
class SimpleMesh:
    vertices: 'np.ndarray[np.float32]'
    indices: 'np.ndarray[np.uint16]'


class WireframeAttributes(ShaderAttributes):
    pos: int


class WireframeUniforms(ShaderUniforms):
    MVP: int
    COLOR: int


class WireframeShader(ShaderCache):

    @cwd(script_dir(__file__), 'shaders')
    def __init__(self):
        self.S = self.compile('wireframe.vert', 'wireframe.frag')
        self.A = WireframeAttributes(self.S)
        self.U = WireframeUniforms(self.S)


class Wireframe:

    def __init__(self, mesh: SimpleMesh, color: glm.vec4, width: float = 1.0):
        self.vertices = VBO(
            mesh.vertices,
            usage=GL_STATIC_DRAW,  # type: ignore
            target=GL_ARRAY_BUFFER,  # type: ignore
        )
        self.indices = VBO(
            mesh.indices.astype(np.uint32),
            usage=GL_STATIC_DRAW,  # type: ignore
            target=GL_ELEMENT_ARRAY_BUFFER,  # type: ignore
        )
        self.shader = WireframeShader.get()
        self.color: 'np.ndarray[np.float32]' = \
            np.array(color, dtype=np.float32)  # type: ignore
        self.width = width

    def render(self, h: Hierarchy):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(self.width)
        size: int = self.indices.size  # type: ignore
        with self.shader.S, self.shader.A, self.vertices, self.indices:
            glUniformMatrix4fv(self.shader.U.MVP, 1, GL_TRUE, h.ptr(h.MVP))
            glUniform4fv(self.shader.U.COLOR, 1, self.color)
            glVertexAttribPointer(
                self.shader.A.pos,  # attribute
                3,                  # size
                GL_FLOAT,           # type
                GL_FALSE,           # normalize
                0,                  # stride    (0 => tighty packed)
                None,               # start     (None => start at 0)
            )
            glDrawElements(GL_TRIANGLES, size, GL_UNSIGNED_INT, ptr(0))
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
