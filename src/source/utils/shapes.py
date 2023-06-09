from functools import cache
from typing import List, cast

import glm
import numpy as np

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

@cache
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


@cache
def sphere(resolution: int = 32):
    """ Sphere Mesh """
    C = np.pi * np.linspace(-1.0, 1.0, resolution, endpoint=False)
    S = np.stack([  # type: ignore
        np.sin(C),
        np.cos(C),
        np.zeros(resolution),
    ], 1)
    R = np.arange(resolution)
    O = np.roll(R, -1)  # type: ignore
    I = np.stack([R, O], 1)
    return Mesh(
        vertices=np.concatenate([
            np.roll(S, 0, 1),  # type: ignore
            np.roll(S, 1, 1),  # type: ignore
            np.roll(S, 2, 1),  # type: ignore
        ]).astype(np.float32),
        indices=np.concatenate([
            (I + 0 * resolution),
            (I + 1 * resolution),
            (I + 2 * resolution),
        ]).astype(np.uint32),
        geometry=Geometry.Lines,
    )


def sphere_2(resolution: int = 32):
    """ Sphere Mesh """
    # Setup Circle Vertices
    radians = np.pi * np.linspace(-1.0, 1.0, resolution, endpoint=False)
    circle = np.stack([  # type: ignore
        np.sin(radians),
        np.cos(radians),
        np.zeros(resolution),
    ], 1)
    # Setup Circle Edges
    R = np.arange(resolution)
    O = np.roll(R, -1)  # type: ignore
    I = np.stack([R, O], 1)

    # Setup Rotations
    L = glm.radians(90)
    H = glm.radians(45)
    X = glm.vec3(1, 0, 0)
    Y = glm.vec3(0, 1, 0)
    Z = glm.vec3(0, 0, 1)

    # Create rotations in numpy
    def rot(angle, vector):
        r = glm.rotate(angle, vector)
        m = np.array(r).T
        return m[:3,:3]

    # Tilt \ | /
    inner = [rot(+H, X), rot(0, X), rot(-H, X)]
    # Orientation | -- O
    outer = [rot(L, Z), rot(L, Y), rot(L, X)]

    # Transform the cicles
    def transform(I, O):
        M = O @ I
        return circle @ M.T
    
    # Build sphere
    vertices = [transform(I, O) for I in inner for O in outer]
    indices = [I + i * resolution for i, _ in enumerate(vertices)]
 
    # Generate OpenGl Mesh
    return Mesh(
        vertices=np.concatenate(vertices).astype(np.float32),
        indices=np.concatenate(indices).astype(np.uint32),
        geometry=Geometry.Lines,
    )
