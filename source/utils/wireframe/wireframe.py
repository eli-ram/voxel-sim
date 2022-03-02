from OpenGL.GL import *
import numpy as np

from .shaders.wireframeshader import WireframeShader
from ..mesh.simplemesh import SimpleMesh
from ..matrices import Hierarchy
from ..buffer import BufferConfig
from ...data.colors import Color, Colors

class Wireframe:

    def __init__(self, mesh: SimpleMesh):
        self._V = BufferConfig('vertices').single(mesh.vertices)
        self._I = BufferConfig('indices').single(mesh.indices.astype(np.uint32))
        self._S = WireframeShader.get()
        self._G = mesh.geometry.value
        self._c = Colors.WHITE
        self._w = 1.0

    def setColor(self, color: Color):
        self._c = color
        return self

    def setWidth(self, width: float):
        self._w = width
        return self

    def render(self, m: Hierarchy):
        V = self._V
        I = self._I
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(self._w)
        with self._S as (A, U), V, I:
            glUniformMatrix4fv(U.MVP, 1, GL_TRUE, m.ptr(m.MVP))
            glUniform4fv(U.COLOR, 1, self._c.value)
            with V as (pos,):
                V.attribute(pos, A.pos)
            with I as (i,):
                I.draw(i, self._G)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


