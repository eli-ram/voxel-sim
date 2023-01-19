from dataclasses import dataclass
from enum import Enum
from OpenGL import GL
from ..types import Array, F, U

class Geometry(Enum):
    Triangles = GL.GL_TRIANGLES
    Lines = GL.GL_LINES


@dataclass
class SimpleMesh:
    vertices: 'Array[F]'
    indices: 'Array[U]'
    geometry: Geometry = Geometry.Triangles