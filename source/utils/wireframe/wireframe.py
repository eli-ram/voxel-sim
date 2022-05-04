from OpenGL.GL import *
import glm
import numpy as np

from .shaders.wireframeshader import WireframeShader
from ...graphics.matrices import Hierarchy
from ...graphics.buffer import BufferConfig
from source.data import (
    mesh as m,
    colors,
)

class Wireframe:
    """ Render A Wireframe """

    def __init__(self, mesh: m.Mesh):
        self._V = BufferConfig('vertices').single(mesh.vertices)
        self._I = BufferConfig('indices').single(mesh.indices)
        self._S = WireframeShader.get()
        self._G = mesh.geometry.value
        self._c = colors.get.WHITE
        self._w = 1.0

    def setColor(self, color: colors.Color):
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
            MVP = m.makeMVP()
            glUniformMatrix4fv(U.MVP, 1, GL_FALSE, glm.value_ptr(MVP))
            glUniform4fv(U.COLOR, 1, self._c.value)
            with V as (pos,):
                V.attribute(pos, A.pos)
            with I as (i,):
                I.draw(i, self._G)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


