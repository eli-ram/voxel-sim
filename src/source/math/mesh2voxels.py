import glm
import source.graphics.matrices as mat
from source.data.mesh import Geometry, Mesh
from .rasterizers.np_raster import Z_Hash_Rasterizer
from .rasterizers.RasterDirection import Raster_Direction_3D

from source.utils.types import int3, Array, F, I, B
from source.debug.time import time

"""
This is basically a (black/white) software-rasterizer.
But, it's for filling a volume instead of a surface.

Resources:
> https://courses.cs.washington.edu/courses/csep557/10au/lectures/triangle_intersection.pdf


"""

@time("mesh_to_voxels")
def mesh_to_voxels(mesh: Mesh, matrix: glm.mat4, shape: int3):
    # Transform mesh into shape
    V, I = _transform(mesh, matrix)
    # Compute for X, Y, Z
    Z = _rasterize(V, I, shape, 'Z')
    X = _rasterize(V, I, shape, 'X')
    Y = _rasterize(V, I, shape, 'Y')
    # Join and return
    return Z & X & Y
 

def _transform(mesh: Mesh, matrix: glm.mat4):
    assert mesh.geometry == Geometry.Triangles, \
        " Mesh must be made up of triangles! "

    # Assure that arrays are formatted correctly
    vertices = mesh.vertices.reshape(-1, 3)
    indices = mesh.indices.reshape(-1, 3)

    T = mat.to_affine(matrix)
    M = T[:, :3]
    V = T[:, 3]
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
