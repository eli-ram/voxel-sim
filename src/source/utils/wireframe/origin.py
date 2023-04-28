from OpenGL import GL
import glm

from .shaders import OriginShader
from source.graphics.matrices import Hierarchy

class Origin:
    """ Render A Wireframe """

    @classmethod
    def cached(cls) -> 'Origin':
        if not hasattr(cls, '__cached'):
            setattr(cls, '__cached', cls())
        return getattr(cls, '__cached')

    def __init__(self):
        self._S = OriginShader.get()
        self._w = 2.0

    def setWidth(self, width: float):
        self._w = width
        return self

    def render(self, m: Hierarchy):
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glLineWidth(self._w)
        with self._S as (A, U):
            MVP = m.makeMVP()
            GL.glUniformMatrix4fv(U.MVP, 1, GL.GL_FALSE, glm.value_ptr(MVP))
            GL.glDrawArrays(GL.GL_POINTS, 0, 1)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)


