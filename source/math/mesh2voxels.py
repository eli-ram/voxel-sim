import numpy as np
from .rasterizers.np_raster import Z_Hash_Rasterizer
from .rasterizers.RasterDirection import Raster_Direction_3D

from ..utils.mesh.simplemesh import Geometry, SimpleMesh
from ..utils.types import int3, Array, F, I

"""
This is basically a (black/white) software-rasterizer.
But, it's optimized for filling a volume instead of a surface.

Resources:
> https://courses.cs.washington.edu/courses/csep557/10au/lectures/triangle_intersection.pdf


"""


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
