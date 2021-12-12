from dataclasses import dataclass
from enum import Enum
from OpenGL.GL import *
from ..types import Array, F, U

class Geometry(Enum):
    Triangles = GL_TRIANGLES
    Lines = GL_LINES


@dataclass
class SimpleMesh:
    vertices: 'Array[F]'
    indices: 'Array[U]'
    geometry: Geometry = Geometry.Triangles