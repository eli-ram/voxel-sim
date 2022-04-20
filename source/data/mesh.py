from typing import NamedTuple
from enum import Enum
from OpenGL.GL import *
import numpy as np


class Geometry(Enum):
    Triangles = GL_TRIANGLES
    Quads = GL_QUADS
    Lines = GL_LINES


class Mesh(NamedTuple):
    vertices: 'np.ndarray[np.float32]'
    indices: 'np.ndarray[np.uint32]'
    geometry: Geometry = Geometry.Triangles
