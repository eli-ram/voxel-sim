from typing import DefaultDict
import numpy as np

from .linalg import coordinates, unpack

from ..utils.wireframe import Geometry, SimpleMesh
from ..utils.types import int3,  Array, F, I

"""
This is basically a (black/white) software-rasterizer.
But, it's optimized for filling a volume instead of a surface.

Resources:
> https://courses.cs.washington.edu/courses/csep557/10au/lectures/triangle_intersection.pdf


"""

class Rasterizer_3D:

    def __init__(self, volume: int3, swizzle: int3 = (2, 1, 0)):
        # Configure swizzle
        x, y, z = swizzle
        self.swizzle: slice = [x, y, z] # type: ignore

        # Configure z-buffer-hash
        self.y_size = volume[y]
        self.hash: dict[int, 'Array[F]'] = \
            DefaultDict(lambda: np.zeros(0, np.float32))

        # Configure xy-space
        self.xy_min: 'Array[F]' = \
            np.zeros(2, np.int32)
        self.xy_max: 'Array[F]' = \
            np.array(list(volume), np.int32)[[x, y]]  # type: ignore

    def grid_index(self, x: int, y: int):
        t = (int(x), int(y), slice(None, None, 1))
        return (t[i] for i in self.swizzle) # type: ignore

    def get(self, I: int):
        x = I % self.y_size
        y = I // self.y_size
        z = np.unique(self.hash[I].round(4))
        return x, y, z

    def hit(self, triangle: 'Array[F]', P: 'Array[F]'):
        """ Check if Points lies inside the triangle 

            Using: Barycentric Coordinates

        """
        # Retrieve triangle XY's
        A, B, C = unpack(triangle[:, :2])
        # print(A, B, C)

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
            + (ay * cx)
            - (ax * cy)
            + (cy - ay) * px
            + (ax - cx) * py
        )

        t = area * (
            + (ax * by)
            - (ay * bx)
            + (ay - by) * px
            + (bx - ax) * py
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

    def cache(self, triangle: 'Array[F]'):
        """ Cache a triangle into the Z-buffers """
        triangle = triangle[:, self.swizzle]
        # print("triangle")

        # Find triangle low bounds
        xy_min = np.floor(np.min(triangle[:, :2], axis=0)).astype(np.int32)
        if not np.all(xy_min <= self.xy_max):
            # print("min is out of bounds")
            return

        # Find triangle high bounds
        xy_max = np.ceil(np.max(triangle[:, :2], axis=0) + 0.01).astype(np.int32)
        if not np.all(xy_max >= self.xy_min):
            # print("max is out of bounds")
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

        I = coords[:, 0] + (coords[:, 1] * self.y_size)

        # Fill Z-buffers
        for i, z in zip(I, P):
            # i = int(i)
            self.hash[i] = np.append(self.hash[i], z)  # type: ignore

    def run(self, indices: 'Array[I]', vertices: 'Array[F]'):
        assert indices.shape[1] == 3, \
            " Indices must be on the form [Nx3] to represent triangles !"
        assert vertices.shape[1] == 3, \
            " Vertices must be on the form [Nx3] to represent vertices !"

        for tri in indices:
            self.cache(vertices[tri, :])

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


def mesh_2_voxels(mesh: SimpleMesh, transform: 'Array[F]', voxels: int3) -> 'Array[F]':
    assert mesh.geometry == Geometry.Triangles, \
        " Mesh must be made up of triangles! "

    assert transform.shape == (3, 4), \
        " Expected [3x4] affine transform matrix "

    # Get Triangles from mesh
    print("[#] Transform")
    M = transform[:, :3]
    V = transform[:, 3]
    VS = mesh.vertices.size // 3
    vertices = mesh.vertices.reshape(VS, 3)
    vertices = (M @ vertices.T).T + V
    IS = mesh.indices.size // 3
    indices = mesh.indices.reshape(IS, 3)

    # Init rasterizer
    rasterizer = Rasterizer_3D(voxels)

    print("[#] Wide Triangles")
    rasterizer.run(indices, vertices)

    # debug
    # rasterizer.points()

    # Voxel Grid to fill / return
    grid = np.zeros(shape=voxels, dtype=np.float32)

    # Z-indexes for Z-axis
    i: int = rasterizer.swizzle[2] # type: ignore
    Z_space = np.arange(voxels[i], dtype=np.float32) + 0.5

    print("[#] Wide Voxels")

    # Potentia Parallel-For
    for I in rasterizer.hash:
        x, y, z = rasterizer.get(I)
        # Find the boolean matrix for voxel-surface-ray-intersection
        B = Z_space[:, np.newaxis] < z[np.newaxis, :]
        # Count ray-intersections
        C: 'np.ndarray[np.uint64]' = \
            np.count_nonzero(B, axis=1)  # type: ignore
        # intersection modulo 2 means that the voxel is inside the mesh
        x, y, z = rasterizer.grid_index(x, y)
        grid[x, y, z] = C % 2

    return grid
