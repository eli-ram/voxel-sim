

from OpenGL.GL import *
import glm
import numpy as np

from .shaders.deformationshader import DeformationShader
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
        self.color = colors.get.WHITE
        self.width = 1.0
        self.buffer = BufferConfig('vertices').combine(mesh.vertices, offset)
        self.indices = BufferConfig('indices').single(mesh.indices.astype(np.uint32))
        self.shader = DeformationShader.get()
        self.deformation = 0.0

    def setColor(self, color: colors.Color):
        self.color = color
        return self

    def setWidth(self, width: float):
        self.width = width
        return self

    def render(self, m: Hierarchy):
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(self.width)
        with self.shader as (A, U):
            MVP = m.makeMVP()
            glUniformMatrix4fv(U.MVP, 1, GL_FALSE, glm.value_ptr(MVP))
            glUniform4fv(U.COLOR, 1, self.color.value)
            glUniform1f(U.DEFORMATION, self.deformation)
            with self.buffer as (pos, offset):
                self.buffer.attribute(pos, A.pos)
                self.buffer.attribute(offset, A.offset)
            with self.indices as (view,):
                self.indices.draw(view, GL_LINES)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


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