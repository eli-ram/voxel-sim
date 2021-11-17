from ..data.truss import Truss
from ..data.voxels import Voxels, Volume, Offset
import numpy as np

__all__ = ['voxels2truss', 'Builder']


def voxels2truss(voxels: Voxels, **options: bool):
    builder = Builder(voxels)
    if options.get('faces', True):
        builder.run(Builder.FACES)
    if options.get('edges', True):
        builder.run(Builder.EDGES)
    if options.get('corners', True):
        builder.run(Builder.CORNERS)
    return builder.output()


def get_range(size: int, offset: int):
    if offset > 0:
        a = slice(0, size - offset)
        b = slice(offset, size)
    else:
        a = slice(-offset, size)
        b = slice(0, size + offset)
    return a, b


def get_ranges(size: Volume, offset: Offset):
    sx, sy, sz = size
    ox, oy, oz = offset
    AX, BX = get_range(sx, ox)
    AY, BY = get_range(sy, oy)
    AZ, BZ = get_range(sz, oz)
    A = (AX, AY, AZ)
    B = (BX, BY, BZ)
    return A, B


class Builder:

    # Offsets to check to assemble the Truss
    FACES: list[Offset] = [
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    ]
    EDGES: list[Offset] = [
        (1, 1, 0),
        (0, 1, 1),
        (1, 0, 1),
        (1, -1, 0),
        (1, 0, -1),
    ]
    CORNERS: list[Offset] = [
        (1, 1, 1),
        (1, 1, -1),
        (1, -1, 1),
        (1, -1, -1),
    ]

    def __init__(self, voxels: Voxels):
        self.edges: 'list[np.ndarray[np.uint32]]' = []
        self.areas: 'list[np.ndarray[np.float32]]' = []
        self.voxels = voxels

    def run(self, offsets: list[Offset]):
        for offset in offsets:
            self.get_edges(offset)

    def get_edges(self, offset: Offset):
        V = self.voxels
        A, B = get_ranges(V.shape, offset)
        connectivity = V.grid[A] & V.grid[B]
        connections = np.nonzero(connectivity)  # type: ignore
        a_vertices = V.index_table[A][connections]
        b_vertices = V.index_table[B][connections]
        a_strength = V.strength[A][connections]
        b_strength = V.strength[B][connections]
        self.edges.append(np.vstack([a_vertices, b_vertices]).T)
        self.areas.append((a_strength + b_strength) / 2)

    def output(self) -> Truss:
        return Truss(
            nodes=self.voxels.vertices,
            forces=self.voxels.force_array(),
            static=self.voxels.static_array(),
            edges=np.vstack(self.edges),
            areas=np.hstack(self.areas),
        )
