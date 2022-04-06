from dataclasses import dataclass
from enum import Enum
from OpenGL.GL import *
import numpy as np

class Geometry(Enum):
    Triangles = GL_TRIANGLES
    Quads = GL_QUADS
    Lines = GL_LINES


@dataclass
class Mesh:
    vertices: np.ndarray[np.float32]
    indices: np.ndarray[np.uint32]
    geometry: Geometry = Geometry.Triangles