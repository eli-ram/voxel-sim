from typing import Any
import numpy as np

from .linalg import coords, normal, unpack

from ..utils.wireframe import Geometry, SimpleMesh
from ..utils.types import int3, int2

"""
This is basically a (black/white) software-rasterizer.
But, it's optimized for filling a volume instead of a surface.

Resources:
> https://courses.cs.washington.edu/courses/csep557/10au/lectures/triangle_intersection.pdf


"""


class _XY_to_Z:
    # Triangle (a, b, c)
    vertices: 'np.ndarray[np.float32]'

    def hit(self, XY: 'np.ndarray[np.float32]'):
        """ Check if Points lies inside the triangle """
        # Retrieve triangle XY's
        A, B, C = unpack(self.vertices[:2, :])

        # Calculate Barycentric Conversion
        T = np.vstack((B - C, A - C))
        M: 'np.ndarray[np.float32]' = np.linalg.inv(T)  # type: ignore

        # Apply to Points
        a, b = unpack(M @ (XY - C))
        c = 1 - a - b

        """
         a = ((by - cy)*(x - cx) + (cx - bx)*(y - cy)) / ((by - cy)*(ax - cx) + (cx - bx)*(ay - cy))
         b = ((cy - ay)*(x - cx) + (ax - cx)*(y - cy)) / ((by - cy)*(ax - cx) + (cx - bx)*(ay - cy))
         c = 1 - a - b
        """

        # Check if conditions is met
        T1 = (0 <= a) & (a <= 1)
        T2 = (0 <= b) & (b <= 1)
        T3 = (0 <= c) & (c <= 1)

        return T1 & T2 & T3

    def proj(self, XY: 'np.ndarray[np.float32]') -> 'np.ndarray[np.float32]':
        """ Project XY onto Triangle plane to find Z """
        A, B, C = unpack(self.vertices)

        # Solve Triangle Plane for Z
        N = normal(A, B, C)
        D = N[2]
        N[2] = np.dot(N, self.a)  # type: ignore
        N[:] /= D

        # Compute Z-array
        return np.dot(N[:2], XY) + N[2]  # type: ignore

    def min_xy(self, low: 'np.ndarray[np.int32]'):
        """ Get min xy-index with low cutoff """
        M = np.min(self.vertices[:2, :], axis=0)
        I = np.floor(M).astype(np.int32)
        L = np.maximum(I, low)
        return L

    def max_xy(self, high: 'np.ndarray[np.int32]'):
        """ Get max xy-index with high cutoff """
        M = np.max(self.vertices[:2, :], axis=0)
        I = np.ceil(M).astype(np.int32)
        L = np.minimum(I, high)
        return L


def range_2D(lx: int, hx: int, ly: int, hy: int):
    rx = range(lx, hx)
    ry = range(ly, hy)
    yield from ((x, y) for y in ry for x in rx)


def mesh_2_voxels(mesh: SimpleMesh, transform: 'np.ndarray[np.float32]', voxels: int3) -> 'np.ndarray[np.float32]':
    assert mesh.geometry == Geometry.Triangles, \
        " Mesh must be made up of triangles! "

    assert transform.shape == (4, 3), \
        " Expected [4x3] affine transform matrix "

    # Hash (x,y) indices to Z-arrays
    xy_hash: dict[int2, 'np.ndarray[np.float32]'] = dict()

    # Add z-value to xy_hash
    def add(x: int, y: int, z: Any):
        key = (x, y)
        arr = xy_hash.get(key)
        if arr is None:
            arr = np.zeros(0, dtype=np.float32)
        xy_hash[key] = np.append(arr, z)  # type: ignore

    # Get Triangles from mesh
    tris = mesh.vertices[mesh.indices]

    # Lowest allowed index
    v_min: 'np.ndarray[np.int32]' = \
        np.zeros(2, dtype=np.int32)  # type: ignore

    # Higest allowed index
    v_max: 'np.ndarray[np.int32]' = \
        np.array(voxels[:2], dtype=np.int32)  # type: ignore

    triangle = _XY_to_Z()

    for tri in tris:
        # Transform Vertices
        vertices = np.append(tri, 1, axis=0)  # type: ignore
        vertices = np.transpose(transform @ vertices)
        # Create support triangle
        triangle.vertices = vertices[:3]
        # Get index-ranges
        lx, ly = triangle.min_xy(v_min)
        hx, hy = triangle.max_xy(v_max)
        # Get relevant coordinates
        coordinates = coords(lx, ly, hx, hy)
        # Center points in the voxels
        points = (coordinates.astype(np.float32) + 0.5).astype(np.float32)
        # Find triangle intersections
        hits = triangle.hit(points)  # type: ignore
        # Find Z-values per intersection
        Z = triangle.proj(points[hits])
        # Fill Z-buffers
        for (x, y), z in zip(unpack(coordinates[hits]), Z):
            add(x, y, z)

    # Voxel Grid to fill / return
    grid = np.zeros(shape=voxels, dtype=np.float32)

    # Z-indexes for Z-axis
    Z_space = np.arange(voxels[2], dtype=np.float32) + 0.5

    for (x, y), Z_points in xy_hash.items():
        # Find the boolean matrix for voxel-surface-ray-intersection
        B = Z_space < Z_points[np.newaxis, :]
        # Count ray-intersections
        C = np.nonzero_count(B, axis=1)  # type: ignore
        # intersection modulo 2 means that the voxel is inside the mesh
        grid[x, y, :] = C % 2

    return grid
