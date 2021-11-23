from typing import Any, Optional
# import numpy.typing as npt # type: ignore
import numpy as np

from ..utils.wireframe import Geometry, SimpleMesh
from ..utils.types import int3, int2

"""
This is basically a (black/white) software-rasterizer.
But, it's optimized for filling a volume instead of a surface.
"""


class Triangle:

    def __init__(self, vertices: 'np.ndarray[np.float32]'):
        assert vertices.shape == (3, 3), \
            "Vertices does not resemble a triangle"
        self.vertices = vertices

    def min_xy(self, low: 'np.ndarray[np.int32]'):
        """ Get min xy-index with low cutoff """
        M = np.min(self.vertices[:2,:], axis=0)
        I = np.floor(M).astype(np.int32)
        L = np.maximum(I, low)
        return L

    def max_xy(self, high: 'np.ndarray[np.int32]'):
        """ Get max xy-index with high cutoff """
        M = np.max(self.vertices[:2,:], axis=0)
        I = np.ceil(M).astype(np.int32)
        L = np.minimum(I, high)
        return L

    def proj_Z(self, X: float, Y: float) -> Optional[float]:
        """ Calculates the point (X, Y, Z) on the triangle
            Returns {Z} if it exists.
        """

def range_2D(lx: int, hx: int, ly:int, hy: int):
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
        xy_hash[key] = np.append(arr, z) # type: ignore

    # Get Triangles from mesh
    tris = mesh.vertices[mesh.indices]

    # Lowest allowed index
    v_min: 'np.ndarray[np.int32]' = \
        np.zeros(2, dtype=np.int32) # type: ignore

    # Higest allowed index
    v_max: 'np.ndarray[np.int32]' = \
        np.array(voxels[:2], dtype=np.int32) # type: ignore
    
    for tri in tris:
        # Transform Vertices
        vertices = np.append(tri, 1, axis=0) # type: ignore
        vertices = np.transpose(transform @ vertices)
        # Create support triangle
        triangle = Triangle(vertices[:3])
        # Get index-ranges
        lx, ly = triangle.min_xy(v_min)
        hx, hy = triangle.max_xy(v_max)
        for x, y in range_2D(lx, hx, ly, hy):
            # Check for z-hit
            z = triangle.proj_Z(x + 0.5, y + 0.5)
            if z is None: continue
            # Cache z-hit
            add(x, y, z)

    # Voxel Grid to fill / return
    grid = np.zeros(shape=voxels, dtype=np.float32)

    # Z-indexes for Z-axis
    Z_space = np.arange(voxels[2], dtype=np.float32) + 0.5

    for (x, y), Z_points in xy_hash.items():
        # Find the boolean matrix for voxel-surface-ray-intersection
        B = Z_space < Z_points[np.newaxis, :]
        # Count ray-intersections
        C = np.nonzero_count(B, axis=1) # type: ignore
        # intersection modulo 2 means that the voxel is inside the mesh
        grid[x,y,:] = C % 2

    return grid