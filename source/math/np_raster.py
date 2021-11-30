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

    def rasterize(self, X: 'Array[F]', Y: 'Array[F]', Z: 'Array[F]'):
        x, y, _ = self.shape

        lx, hx = minmax(X, x)
        if lx == hx:
            return

        ly, hy = minmax(Y, y)
        if ly == hy:
            return

        try:
            B, BX, BY = barycentric(X, Y)
        except ZeroDivisionError:
            return 
            
        bz = glm.vec3(Z[0], Z[1], Z[2])

        # Setup barycentric coord in (lx, ly)
        by = B + BY * (ly + 0.5) + BX * (lx + 0.5)

        # Iterate y
        for y in range(ly, hy):
            # Get Barycentric coord for (lx, y)
            bx = by
            # Iterate x
            for x in range(lx, hx):
                b = bx
                # Check if inside triangle
                if b.x >= 0 and b.y >= 0 and b.z >= 0:
                    # Compute interpolated z
                    z = glm.dot(b, bz)
                    # Store z
                    self.plot(x, y, z)

                # Iterate Barycentric coord over x
                bx = bx + BX

            # Iterate Barycentric coord over y
            by = by + BY


    @time("np-raster-run")
    def run(self, indices: 'Array[I]', vertices: 'Array[F]'):
        assert indices.shape[1] == 3, \
            " Indices must be on the form [Nx3] to represent triangles !"

        assert vertices.shape[1] == 3, \
            " Vertices must be on the form [Nx3] to represent vertices !"

        for tri in indices:
            X, Y, Z = unpack(vertices[tri, :].transpose())
            self.rasterize(X, Y, Z)

    def voxels(self):
        # Voxel Grid to fill / return
        grid = np.zeros(self.shape, np.float32)

        # Z-indexes for Z-axis
        s = np.arange(self.height, dtype=np.float32) + 0.5

        for i in self.zhash:
            x, y, z = self.get(i)
            if z.size == 1:
                print("cut")
                continue
            # Find the boolean matrix for voxel-surface-ray-intersection
            B = s[:, np.newaxis] <= z[np.newaxis, :]
            # Count ray-intersections
            C: 'Array[I]' = \
                np.count_nonzero(B, axis=1)  # type: ignore
            # intersection modulo 2 means that the voxel is inside the mesh
            grid[x, y, :] = C % 2

        return grid

def minmax(V: 'Array[F]', h: int):
    lv = max(round(V.min()), 0)
    hv = min(round(V.max()), h)
    return lv, hv

def barycentric(X: 'Array[F]', Y: 'Array[F]'):
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
        ::XY => [x[], y[]]

    Returns:
        ::B => barycentric Origin
        ::Bx => barycentrix X unit vector
        ::By => barycentric Y unit vector
    """

    # Get X, Y Arrays
    x0, x1, x2 = X
    y0, y1, y2 = Y
    X0 = glm.vec3(x1, x2, x0)
    X1 = glm.vec3(x2, x0, x1)
    Y0 = glm.vec3(y1, y2, y0)
    Y1 = glm.vec3(y2, y0, y1)
    
    # Calculate doubled signed area
    area = glm.dot(X0, Y1) - glm.dot(Y0, X1)
    # print(area)

    # Require area
    if area == 0.0:
        raise ZeroDivisionError("Cannot compute for zero area!")

    # Inverted signed area
    area = 1.0 / area

    # Barycentric Base
    B = (X0 * Y1 - Y0 * X1) * area

    # Barycentric X
    BX = (Y0 - Y1) * area

    # Barycentric Y
    BY = (X1 - X0) * area

    # Return Linear set
    return B, BX, BY

