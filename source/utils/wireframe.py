from enum import Enum
from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
from dataclasses import dataclass
from .shaders import (
    ShaderAttributes,
    ShaderUniforms,
    ShaderCache,
)
from .directory import cwd, script_dir
from .matrices import Hierarchy
import numpy as np
import glm


class Geometry(Enum):
    Triangles = GL_TRIANGLES
    Lines = GL_LINES


@dataclass
class SimpleMesh:
    vertices: 'np.ndarray[np.float32]'
    indices: 'np.ndarray[np.uint32]'
    geometry: Geometry = Geometry.Triangles


class WireframeAttributes(ShaderAttributes):
    pos: int


class WireframeUniforms(ShaderUniforms):
    MVP: int
    COLOR: int


class WireframeShader(ShaderCache):

    @cwd(script_dir(__file__), 'shaders')
    def __init__(self):
        self.S = self.compile(
            'wireframe.vert',
            # 'wireframe.geom',
            'wireframe.frag',
        )
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
        self.geometry = mesh.geometry.value

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
            glDrawElements(
                self.geometry,      # geometry type
                size,               # geometry count
                GL_UNSIGNED_INT,    # index type
                None,               # index start (None => start at 0)
            )
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def delete(self):
        self.vertices.delete()
        self.indices.delete()


def origin(size: float):
    P = +size
    M = -size
    return SimpleMesh(
        vertices=np.array([  # type: ignore
            [0, 0, P],
            [0, 0, M],
            [0, P, 0],
            [0, M, 0],
            [P, 0, 0],
            [M, 0, 0],
        ], np.float32),
        indices=np.array([  # type: ignore
            [0, 1],
            [2, 3],
            [4, 5],
        ], np.uint32),
        geometry=Geometry.Lines,
    )


def line_cube():
    return SimpleMesh(
        vertices=np.array([  # type: ignore
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [1, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [0, 1, 1],
            [1, 1, 1],
        ], np.float32),
        indices=np.array([  # type: ignore
            [0, 1],
            [0, 2],
            [0, 4],
            [7, 3],
            [7, 5],
            [7, 6],
            [1, 3],
            [3, 2],
            [2, 6],
            [6, 4],
            [4, 5],
            [5, 1],
        ], np.uint32),
        geometry=Geometry.Lines
    )


def simplex():
    return SimpleMesh(
        vertices=np.array([  # type: ignore
            [0, 0, 0],
            [0.5, 1.0, 0],
            [0.5, 0.5, 5],
            [1.0, 0.5, 0],
        ], np.float32),
        indices=np.array([  # type: ignore
            [0, 1, 2],
            [1, 2, 3],
            [2, 3, 0],
            [3, 0, 1],
        ], np.uint32),
        geometry=Geometry.Triangles,
    )
