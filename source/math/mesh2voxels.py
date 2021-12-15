from typing import DefaultDict
from enum import Enum
import numpy as np
from source.math.np_raster import Z_Hash_Rasterizer

from source.math.scanline import IntRasterizer

from .linalg import coordinates, unpack

from ..utils.mesh.simplemesh import Geometry, SimpleMesh
from ..utils.types import int3,  Array, F, I
from ..debug.time import time

"""
This is basically a (black/white) software-rasterizer.
But, it's optimized for filling a volume instead of a surface.

Resources:
> https://courses.cs.washington.edu/courses/csep557/10au/lectures/triangle_intersection.pdf


"""


class Raster_Direction_3D(Enum):
    X = (1, 2, 0), (2, 0, 1)
    Y = (2, 0, 1), (1, 2, 0)
    Z = (0, 1, 2), (0, 1, 2)

    @property
    def swizzle(self) -> slice:
        return self.value[0]

    @property
    def transpose(self) -> int3:
        return self.value[1]

    def reshape(self, shape: int3) -> int3:
        S = [shape[i] for i in self.value[0]]
        return tuple(S)  # type: ignore


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


class Rasterizer_3D:

    def __init__(self, shape: int3):
        self.shape = sx, sy, sz = shape

        # Store Z-height
        self.height = sz

        # Configure z-buffer-hash
        self.empty = np.zeros(0, np.float32)
        self.stride = sx
        self.hash: dict[int, 'Array[F]'] = \
            DefaultDict(lambda: self.empty)

        # Configure xy-space
        self.xy_min = np.zeros(2, np.int32)
        self.xy_max = np.zeros(2, np.int32)
        self.xy_max[:] = [sx, sy]

    def get(self, I: int):
        x = I % self.stride
        y = I // self.stride
        z = np.unique(self.hash[I])
        return x, y, z

    def hit(self, triangle: 'Array[F]', P: 'Array[F]'):
        """ Check if Points lies inside the triangle

            Using: Barycentric Coordinates

        """
        # Retrieve triangle XY's
        A, B, C = unpack(triangle[:, :2])

        # Unpack
        ax, ay = A
        bx, by = B
        cx, cy = C
        px, py = P.T

        # signed (double) area
        area = (
            + (ax * by)
            + (bx * cy)
            + (cx * ay)
            - (ax * cy)
            - (bx * ay)
            - (cx * by)
        )

        # Avoid dividing by 0
        if area == 0.0:
            return

        # inverse signed area
        area = 1 / area

        # barycentric coords
        s = area * (
            + (cy - ay) * px
            + (ax - cx) * py
            + (ay * cx) - (ax * cy)
        )

        t = area * (
            + (ay - by) * px
            + (bx - ax) * py
            + (ax * by) - (ay * bx)
        )

        return (s >= 0) & (t >= 0) & (1-s-t >= 0)

    def proj(self, triangle: 'Array[F]', P: 'Array[F]'):
        """ Project XY onto Triangle plane to find Z """
        A, B, C = unpack(triangle)

        # Find [non-normalized] normal vector
        AB = B - A
        AC = C - A
        N: 'Array[F]' = np.cross(AB, AC)  # type: ignore

        # Solve Triangle Plane for Z
        D = N[2]
        N[2] = np.dot(N, A)  # type: ignore
        N /= D  # type: ignore

        # Compute Z-array
        V: 'Array[F]' = np.dot(P, N[:2])  # type: ignore
        return N[2] - V

    def rasterize(self, triangle: 'Array[F]'):
        """ Cache a triangle into the Z-buffers """

        # Find triangle low bounds
        xy_min = np.round(np.min(triangle[:, :2], axis=0)).astype(np.int32)
        if not np.all(xy_min <= self.xy_max):
            # print("min is out of bounds")
            return

        # Find triangle high bounds
        xy_max = np.round(np.max(triangle[:, :2], axis=0)).astype(np.int32)
        if not np.all(xy_max >= self.xy_min):
            # print("max is out of bounds")
            return

        if not np.all(xy_max > xy_min):
            # print("no space between max and min")
            return

        # Get coordinates & points around the triangle
        lx, ly = np.maximum(xy_min, self.xy_min)
        hx, hy = np.minimum(xy_max, self.xy_max)
        coords = coordinates(lx, hx, ly, hy)
        points = coords + 0.5

        # Get boolean hit array
        hits = self.hit(triangle, points)
        if not np.any(hits):  # type: ignore
            # print("no hits")
            return

        """
        sx = int(hx - lx)
        sy = int(hy - ly)
        H = hits.reshape(sy, sx)
        print("\n".join(" ".join(l) for l in np.where(H, '#', '.')))
        """

        # Cut away coordinates & points that misses
        coords = coords[hits, :]
        points = points[hits, :]

        # Calculate points on the triangle plane
        P = self.proj(triangle, points)

        I = coords[:, 0] + (coords[:, 1] * self.stride)

        # Fill Z-buffers
        for i, z in zip(I, P):
            # i = int(i)
            self.hash[i] = np.append(self.hash[i], z)  # type: ignore

    @time("3D-raster-run")
    def run(self, indices: 'Array[I]', vertices: 'Array[F]'):
        assert indices.shape[1] == 3, \
            " Indices must be on the form [Nx3] to represent triangles !"

        assert vertices.shape[1] == 3, \
            " Vertices must be on the form [Nx3] to represent vertices !"

        for tri in indices:
            self.rasterize(vertices[tri, :])

    def voxels(self):
        # Voxel Grid to fill / return
        grid = np.zeros(self.shape, np.bool_)

        # Z-indexes for Z-axis
        s = np.arange(self.height, dtype=np.float32) + 0.5

        for i in self.hash:
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

    def points(self):

        count = sum(l.size for l in self.hash.values())
        i = 0

        points = np.zeros((count, 3), np.float32)
        for I in self.hash:
            x, y, z = self.get(I)
            XY = np.array([x, y, 1]) + 0.5  # type: ignore
            print(x, y, z)
            for v in z:
                XY[2] = v
                points[i, :] = XY
                i += 1

        return points


def transform(mesh: SimpleMesh, transform: 'Array[F]'):
    assert mesh.geometry == Geometry.Triangles, \
        " Mesh must be made up of triangles! "

    assert transform.shape == (3, 4), \
        " Expected [3x4] affine transform matrix "

    # Assure that arrays are formatted correctly
    vertices = mesh.vertices.reshape(-1, 3)
    indices = mesh.indices.reshape(-1, 3)

    M = transform[:, :3]
    V = transform[:, 3]
    vertices = (M @ vertices.T).T + V

    return vertices, indices


def mesh_2_voxels(vertices: 'Array[F]', indices: 'Array[I]', voxels: int3, direction: str = "Z") -> 'Array[np.bool_]':
    D = Raster_Direction_3D[direction]

    # Init rasterizer
    # rasterizer = Rasterizer_3D(D.reshape(voxels))
    # rasterizer = Z_Raster(D.reshape(voxels))
    rasterizer = Z_Hash_Rasterizer(D.reshape(voxels))

    print("[#] Wide Triangles")
    # Potential Parallel-For
    # Swizzle coordinates
    rasterizer.run(indices, vertices[:, D.swizzle])

    print("[#] Wide Voxels")
    # Potential Parallel-For
    grid = rasterizer.voxels()

    # Restore grid from swizzling
    grid: 'Array[F]' = grid.transpose(D.transpose)  # type: ignore

    return grid
