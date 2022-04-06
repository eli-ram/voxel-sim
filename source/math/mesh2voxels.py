from source.data.mesh import Geometry, Mesh
from .utils import remove_padding_grid
from .rasterizers.np_raster import Z_Hash_Rasterizer
from .rasterizers.RasterDirection import Raster_Direction_3D

from ..utils.types import int3, Array, F, I, B
from ..debug.time import time

"""
This is basically a (black/white) software-rasterizer.
But, it's for filling a volume instead of a surface.

Resources:
> https://courses.cs.washington.edu/courses/csep557/10au/lectures/triangle_intersection.pdf


"""

@time("mesh_to_voxels")
def mesh_to_voxels(mesh: Mesh, transform: 'Array[F]', voxels: int3):
    V, I = _transform(mesh, transform)
    Z = _rasterize(V, I, voxels, 'Z')
    X = _rasterize(V, I, voxels, 'X')
    Y = _rasterize(V, I, voxels, 'Y')
    return remove_padding_grid(Z & X & Y)
 

def _transform(mesh: Mesh, transform: 'Array[F]'):
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


def _rasterize(vertices: 'Array[F]', indices: 'Array[I]', voxels: int3, direction: str) -> 'Array[B]':
    D = Raster_Direction_3D[direction]

    # Init rasterizer
    # Tested to be the 'fastest'
    rasterizer = Z_Hash_Rasterizer(D.reshape(voxels)) 

    # Potential Parallel-For
    # Swizzle coordinates
    rasterizer.run(indices, vertices[:, D.swizzle])

    # Potential Parallel-For
    grid = rasterizer.voxels()

    # Restore grid from swizzling
    return D.transpose(grid)
