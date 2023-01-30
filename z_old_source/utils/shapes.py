from typing import List, cast
import numpy as np
from numpy import dtype
from source.data.mesh import Geometry, Mesh

def _v(*values: List[float]):
    return np.array(cast(list, values), np.float32)

def _i(*values: List[int]):
    return np.array(cast(list, values), np.uint32)

def origin_marker(size: float = 1.0):
    """ A 3D marker for a origin """
    P = +size
    M = -size
    return Mesh(
        vertices=_v(
            [0, 0, P],
            [0, 0, M],
            [0, P, 0],
            [0, M, 0],
            [P, 0, 0],
            [M, 0, 0],
        ),
        indices=_i(
            [0, 1],
            [2, 3],
            [4, 5],
        ),
        geometry=Geometry.Lines,
    )


def line_cube():
    """ A edge frame of a cube """
    return Mesh(
        vertices=_v(
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0],
            [1, 1, 0],
            [0, 0, 1],
            [1, 0, 1],
            [0, 1, 1],
            [1, 1, 1],
        ),
        indices=_i(
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
        ),
        geometry=Geometry.Lines
    )


def simplex():
    """ Triangle pyramide """
    return Mesh(
        vertices=_v(
            [0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.4, 0.4, 0.5],
            [1.0, 0.0, 0.0],
        ),
        indices=_i(
            [0, 1, 2],
            [1, 2, 3],
            [2, 3, 0],
            [3, 0, 1],
        ),
        geometry=Geometry.Triangles,
    )

def sphere(resolution: int = 32):
    """ Sphere Mesh """
    C = np.pi * np.linspace(-1.0, 1.0, resolution, endpoint=False)
    S = np.stack([ # type: ignore
        np.sin(C), 
        np.cos(C), 
        np.zeros(resolution),
    ], 1)
    R = np.arange(resolution)
    O = np.roll(R, -1) # type: ignore
    I = np.stack([R, O], 1)
    return Mesh(
        vertices=np.concatenate([
            np.roll(S, 0, 1), # type: ignore
            np.roll(S, 1, 1), # type: ignore
            np.roll(S, 2, 1), # type: ignore
        ]).astype(np.float32),
        indices=np.concatenate([
            (I + 0 * resolution),
            (I + 1 * resolution),
            (I + 2 * resolution),
        ]).astype(np.uint32),
        geometry=Geometry.Lines,
    )