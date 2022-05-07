from typing import List, NamedTuple
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


def v(*values: List[float]):
    return np.array(list(values), np.float32)

def i(*values: List[int]):
    return np.array(list(values), np.uint32)