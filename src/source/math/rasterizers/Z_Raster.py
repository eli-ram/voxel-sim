from ...debug.time import time
from ...utils.types import int3, Array, F, I
from .scanline import IntRasterizer
from typing import DefaultDict
import numpy as np

class Z_Raster(IntRasterizer):

    def __init__(self, shape: int3):
        super().__init__(shape[:2])
        self.shape = shape
        self.stride = shape[0]
        self.empty = np.zeros(0, np.float32)
        self.zhash: dict[int, 'Array[F]'] = \
            DefaultDict(lambda: self.empty)
        self.height = shape[2]

    def plot(self, x: int, y: int, z: float):
        I = x + y * self.stride
        self.zhash[I] = np.append(self.zhash[I], z)  # type: ignore

    def get(self, I: int):
        x = I % self.stride
        y = I // self.stride
        z = np.unique(self.zhash[I])
        return x, y, z

    @time("z-raster-run")
    def run(self, indices: 'Array[I]', vertices: 'Array[F]'):
        assert indices.shape[1] == 3, \
            " Indices must be on the form [Nx3] to represent triangles !"

        assert vertices.shape[1] == 3, \
            " Vertices must be on the form [Nx3] to represent vertices !"

        for tri in indices:
            A, B, C = vertices[tri, :]
            self.rasterize(A, B, C)  # type: ignore

    def voxels(self):
        # Voxel Grid to fill / return
        grid = np.zeros(self.shape, np.float32)

        # Z-indexes for Z-axis
        s = np.arange(self.height, dtype=np.float32) + 0.5

        for i in self.zhash:
            x, y, z = self.get(i)
            # Cull non-watertight
            if z.size < 2:
                # print("Culled Watertight", z)
                continue
            # Find the boolean matrix for voxel-surface-ray-intersection
            B = s[:, np.newaxis] <= z[np.newaxis, :]
            # Count ray-intersections
            C: 'Array[I]' = \
                np.count_nonzero(B, axis=1)  # type: ignore
            # intersection modulo 2 means that the voxel is inside the mesh
            grid[x, y, :] = C % 2

        return grid

