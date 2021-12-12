import numpy as np
from .simplemesh import SimpleMesh, Geometry

def origin(size: float):
    """ A 3D marker for a origin """
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
    """ A edge frame of a cube """
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
    """ Triangle pyramide """
    return SimpleMesh(
        vertices=np.array([  # type: ignore
            [0, 0, 0],
            [0.5, 1.0, 0],
            [0.5, 0.5, 1],
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
