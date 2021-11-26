from ..data.truss import Truss
from ..data.voxels import Voxels, int3
import numpy as np

__all__ = ['voxels2truss', 'TrussBuilder']


def voxels2truss(voxels: Voxels, exclude: list[str] = []):
    builder = TrussBuilder(voxels)
    if 'faces' not in exclude:
        builder.run(TrussBuilder.FACES)
    if 'edges' not in exclude:
        builder.run(TrussBuilder.EDGES)
    if 'corners' not in exclude:
        builder.run(TrussBuilder.CORNERS)
    return builder.output()


def get_range(size: int, offset: int):
    if offset > 0:
        a = slice(0, size - offset)
        b = slice(offset, size)
    else:
        a = slice(-offset, size)
        b = slice(0, size + offset)
    return a, b


def get_ranges(size: int3, offset: int3):
    sx, sy, sz = size
    ox, oy, oz = offset
    AX, BX = get_range(sx, ox)
    AY, BY = get_range(sy, oy)
    AZ, BZ = get_range(sz, oz)
    A = (AX, AY, AZ)
    B = (BX, BY, BZ)
    return A, B


class TrussBuilder:

    # Offsets to check to assemble the Truss
    FACES: list[int3] = [
        # 6 faces / 2 = 3
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    ]
    EDGES: list[int3] = [
        # 12 edges / 2 = 6
        (1, 1, 0),
        (0, 1, 1),
        (1, 0, 1),
        (1, -1, 0),
        (1, 0, -1),
        (0, 1, -1),
    ]
    CORNERS: list[int3] = [
        # 8 corners / 2 = 4
        (1, 1, 1),
        (1, 1, -1),
        (1, -1, 1),
        (1, -1, -1),
    ]

    def __init__(self, voxels: Voxels):
        self.edges: 'list[np.ndarray[np.uint32]]' = []
        # Grid Shape
        self.shape = voxels.shape
        # Voxel Indices
        I = np.nonzero(voxels.grid) # type: ignore
        # Material Grid
        self.grid = voxels.grid
        # Vertex Array
        self.vertices = np.vstack(I).astype(np.float32).transpose()
        self.vertices += np.float32(0.5)
        # Grid => Vertex Index
        self.index_table = np.zeros(voxels.shape, np.uint32)
        self.index_table[I] = range(len(self.vertices))
        # Force Per Vertex
        self.forces = voxels.forces[I]
        # Strength Per Vertex
        self.strength = voxels.strength[I]
        # Static Locks Per Vertex
        Materials: slice = voxels.grid[I] # type: ignore
        Mapping = voxels.static_map()
        self.static = Mapping[Materials, :]

    def run(self, offsets: list[int3]):
        for offset in offsets:
            self.get_edges(offset)

    def get_edges(self, offset: int3):
        A, B = get_ranges(self.shape, offset)
        connectivity = self.grid[A] & self.grid[B]
        connections = np.nonzero(connectivity)  # type: ignore
        a_vertices = self.index_table[A][connections]
        b_vertices = self.index_table[B][connections]
        self.edges.append(np.vstack([a_vertices, b_vertices]).T)

    def output(self) -> Truss:
        edges = np.vstack(self.edges)
        areas = np.sum(self.strength[edges], axis=0) / 2
        return Truss(
            nodes=self.vertices,
            forces=self.forces,
            static=self.static,
            edges=edges,
            areas=areas,
        )
