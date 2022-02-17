from OpenGL.GL import *
import numpy as np
import glm


from .shaders.wireframeshader import WireframeShader
from ..mesh.simplemesh import SimpleMesh
from ..matrices import Hierarchy
from ..buffer import BufferConfig


class Wireframe:

    def __init__(self, mesh: SimpleMesh, color: glm.vec4, width: float = 1.0):
        self.vertices = BufferConfig('vertices').single(mesh.vertices)
        self.indices = BufferConfig('indices').single(mesh.indices.astype(np.uint32))
        self.shader = WireframeShader.get()
        self.color = np.array([*color], np.float32)  # type: ignore
        self.width = width
        self.geometry = mesh.geometry.value

    def render(self, m: Hierarchy):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(self.width)
        with self.shader as (A, U), self.vertices, self.indices:
            glUniformMatrix4fv(U.MVP, 1, GL_TRUE, m.ptr(m.MVP))
            glUniform4fv(U.COLOR, 1, self.color)
            with self.vertices as (pos,):
                self.vertices.attribute(pos, A.pos)
            with self.indices as (i,):
                self.indices.draw(i, self.geometry)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


