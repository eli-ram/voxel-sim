from OpenGL.GL import *
import glm

from .shaders import OriginShader
from source.graphics.matrices import Hierarchy

class Origin:
    """ Render A Wireframe """

    def __init__(self):
        self._S = OriginShader.get()
        self._w = 2.0

    def setWidth(self, width: float):
        self._w = width
        return self

    def render(self, m: Hierarchy):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(self._w)
        with self._S as (A, U):
            MVP = m.makeMVP()
            glUniformMatrix4fv(U.MVP, 1, GL_FALSE, glm.value_ptr(MVP))
            glDrawArrays(GL_POINTS, 0, 1)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


