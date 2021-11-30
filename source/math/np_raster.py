from collections import defaultdict

from source.debug.time import time
from ..utils.types import int3, Array, F, I
from .linalg import unpack
import numpy as np
import glm

EMPTY = np.zeros(0, np.float32)


class Z_Hash_Rasterizer:

    def __init__(self, shape: int3):
        self.shape = x, y, z = shape
        self.stride = x
        self.height = z
        self.zhash: dict[int, 'Array[F]'] = \
            defaultdict(lambda: EMPTY)
        self.xy_min = np.zeros(2, np.int32)
        self.xy_max = np.zeros(2, np.int32)
        self.xy_max[:] = x, y

    def plot(self, x: int, y: int, z: float):
        I = x + y * self.stride
        self.zhash[I] = np.append(self.zhash[I], z)  # type: ignore

    def get(self, I: int):
        x = I % self.stride
        y = I // self.stride
        z = np.unique(self.zhash[I])
        return x, y, z

    def rasterize(self, triangle: 'Array[F]'):
        xy_min = np.floor(np.min(triangle[:, :2], axis=0)).astype(np.int32)
        if not np.all(xy_min <= self.xy_max):
            return
        xy_max = np.ceil(np.max(triangle[:, :2], axis=0)).astype(np.int32)
        if not np.all(xy_max >= self.xy_min):
            return
        if not np.all(xy_min < xy_max):
            return
        lx, ly = np.maximum(xy_min, self.xy_min)
        hx, hy = np.minimum(xy_max, self.xy_max)

        try:
            B, Bx, By = barycentric(triangle)
        except ZeroDivisionError:
            # There was no area
            return

        Z = glm.vec3(*triangle[:, 2])

        # Setup barycentric coord in (lx, ly)
        b_y = B + By * (ly + 0.5) + Bx * (lx + 0.5)

        # Iterate y
        for y in range(ly, hy):
            # Get Barycentric coord for (lx, y)
            b_x = b_y + 0.0 # type: ignore
            # Iterate x
            for x in range(lx, hx):
                # Check if inside triangle
                if b_x.x >= 0 and b_x.y >= 0 and b_x.z >= 0: # type: ignore
                    # Compute interpolated z
                    z: float = glm.dot(b_x, Z)
                    # Store z
                    self.plot(x, y, z)
                # Iterate Barycentric coord over x
                b_x += Bx
            # Iterate Barycentric coord over y
            b_y += By

    @time("np-raster-run")
    def run(self, indices: 'Array[I]', vertices: 'Array[F]'):
        assert indices.shape[1] == 3, \
            " Indices must be on the form [Nx3] to represent triangles !"

        assert vertices.shape[1] == 3, \
            " Vertices must be on the form [Nx3] to represent vertices !"

        for tri in indices:
            self.rasterize(vertices[tri, :])

    def voxels(self):
        # Voxel Grid to fill / return
        grid = np.zeros(self.shape, np.float32)

        # Z-indexes for Z-axis
        s = np.arange(self.height, dtype=np.float32) + 0.5

        for i in self.zhash:
            x, y, z = self.get(i)
            print(x, y, z)
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


def barycentric(convex: 'Array[F]'):
    """ Compute the Barycentric linear set for any convex polygon

    To get the Barycentric coordinate for (x,y):
        Bc = B + Bx * x + By * y

    To check if a point is inside the convex shape:
        Bc => 0

    To Interpolate a value inside the convex shape:
        V: attribute array (value for every point on the shape)
        v = glm.dot(Bc, V)

        # NOTE: this does not take perspective transforms into account!

    Args:
        ::convex => list[(x, y, ...)]

    Returns:
        ::B => barycentric Origin
        ::Bx => barycentrix X unit vector
        ::By => barycentric Y unit vector
    """

    # Get X, Y Arrays
    (x0, y0), (x1, y1), (x2, y2) = unpack(convex[:, :2])
    X0 = glm.vec3(x0, x1, x2)
    X1 = glm.vec3(x1, x2, x0)
    Y0 = glm.vec3(y0, y1, y2)
    Y1 = glm.vec3(y1, y2, y0)
    
    # Calculate doubled signed area
    area = glm.dot(X0, Y1) - glm.dot(Y0, X1)

    # Require area
    if area == 0.0:
        raise ZeroDivisionError("Cannot compute for zero area!")

    # Inverted signed area
    area = 1 / area

    # Barycentric Base
    B: glm.vec3 = glm.mul(area, X0 * Y1 - Y0 * X1)

    # Barycentric X
    Bx: glm.vec3 = glm.mul(area, Y1 - Y0)

    # Barycentric Y
    By: glm.vec3 = glm.mul(area, X0 - X1)

    # Return Linear set
    return B, Bx, By

