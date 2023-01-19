

from OpenGL import GL
import glm
import numpy as np

from .shaders import DeformationShader
from ...graphics.matrices import Hierarchy
from ...graphics.buffer import BufferConfig

from source.data import (
    mesh as m,
    colors,
)

class DeformationWireframe:

    def __init__(self, mesh: m.Mesh, offset: 'np.ndarray[np.float32]'):
        assert mesh.geometry == m.Geometry.Lines, \
            "Is only defined for lines!"
        assert mesh.vertices.shape == offset.shape, \
            "Offsets must match vertices!"
        self._V = BufferConfig('vertices').combine(mesh.vertices, offset)
        self._I = BufferConfig('indices').single(mesh.indices.astype(np.uint32))
        self._S = DeformationShader.get()
        self._G = mesh.geometry.value
        self._c = colors.get.WHITE # Should not be an attribute of the wireframe !
        self._w = 1.0
        self._d = 0.0

    def setColor(self, color: colors.Color):
        self._c = color
        return self

    def setWidth(self, width: float):
        self._w = width
        return self

    def setDeformation(self, deformation: float):
        self._d = deformation
        return self

    def render(self, m: Hierarchy):
        V = self._V
        I = self._I
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glLineWidth(self._w)
        with self._S as (A, U):
            MVP = m.makeMVP()
            GL.glUniformMatrix4fv(U.MVP, 1, GL.GL_FALSE, glm.value_ptr(MVP))
            GL.glUniform4fv(U.COLOR, 1, self._c.value)
            GL.glUniform1f(U.DEFORMATION, self._d)
            # Bind vertex position & offset
            with V as (pos, offset):
                V.attribute(pos, A.pos)
                V.attribute(offset, A.offset)
            # Draw indices
            with I as (view,):
                I.draw(view, GL.GL_LINES)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)


def test_case():
    from ...data.truss import Truss
    from ...math.truss2stress import fem_simulate

    T = Truss(
        # Node attrs
        nodes=np.array([  # type: ignore
            [0, 0, 0],
            [0.1, 1, 0],
            [0, 2, 0],
            [1, 0, 0],
            [0.9, 1, 0],
            [1, 2, 0],
        ], np.float32),
        forces=np.array([  # type: ignore
            [0, 0, 0],
            [1, 0, 0],
            [-1, 0, 0],
            [0, 0, 0],
            [1, 0, 0],
            [-1, 0, 0],
        ], np.float32),
        static=np.array([  # type: ignore
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 1],
            [0, 0, 1],
        ], np.bool_),
        # Edge attrs
        edges=np.array([  # type: ignore
            # 0-row
            [0, 1],
            [1, 2],
            # 1-row
            [3, 4],
            [4, 5],
            # columns
            [0, 3],
            [1, 4],
            [2, 5],
            # crosses
            [0, 4],
            [2, 4],
            [1, 3],
            [1, 5],
        ], np.uint32),
        areas=np.array([  # type: ignore
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
        ], np.float32),
    )

    D, _ = fem_simulate(T, 1E1)

    M = m.Mesh(T.nodes, T.edges, m.Geometry.Lines)

    return DeformationWireframe(M, D).setWidth(5.0)