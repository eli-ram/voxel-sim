import glm
import numpy as np

import source.data.mesh as m
import source.math.utils as u
import source.utils.shapes as s
import source.graphics.matrices as mat
import source.data.voxel_tree.node as n

from .geometry import Geometry, Context


def _coords(box: n.Box):
    # Bounds
    P = zip(box.start, box.stop)
    # Ranges
    R = (np.arange(l, h) for l, h in P)
    # Grids (can numpy fix meshgrid typing ....)
    G = np.meshgrid(*R)  # type: ignore
    # Unraveled
    U = tuple(np.ravel(i) for i in G)
    # Joined
    return np.vstack(U).astype(np.int64)


def _voxels(ctx: Context):
    # Centered coordinates
    C = _coords(ctx.box) + 0.5
    # Get affine matrix
    T = mat.to_affine(
        # Invert coordinate space
        glm.affineInverse(ctx.matrix) *
        # Fix center
        glm.translate(-glm.vec3(ctx.box.start))
    )
    # mat3 part
    M = T[:, :3]
    # vec3 part
    V = T[:, 3:] # .transpose()
    # Affine transform to local coords
    # FIXME (what went wrong here ...)
    L = (M @ C) + V #[:, np.newaxis]
    # Inside unit circle
    U = np.sum(L * L, axis=0) < 1.0
    # Reshape to grid
    G = U.astype(np.bool_).reshape(ctx.box.shape)
    G = G.swapaxes(0, 1)
    # Remove padding
    return u.remove_padding_grid(G)


class Sphere(Geometry, type='sphere-old'):
    """ A unit sphere """

    __node: n.VoxelNode

    def getMesh(self) -> m.Mesh:
        return s.sphere()

    def getVoxels(self, ctx: Context) -> n.VoxelNode:
        ctx, old = self._cacheCtx(ctx)
        if ctx.eq(old):
            return self.__node

        return super().getVoxels(ctx)


class Sphere2(Geometry, type='sphere'):
    """ A unit sphere """

    __node: n.VoxelNode

    def getMesh(self) -> m.Mesh:
        return s.sphere_2(64)

    def getVoxels(self, ctx: Context) -> n.VoxelNode:
        ctx, old = self._cacheCtx(ctx)
        if ctx.eq(old):
            return self.__node

        # Compute voxels
        offset, grid = _voxels(ctx)
        # Get material
        M = self.material.get()
        # Package Data
        D = n.Data(
            box=n.Box.OffsetShape(offset, grid.shape),
            mask=grid,
            material=(grid * M.id).astype(np.uint32),
            strength=(grid * M.strenght).astype(np.float32),
        )
        # Get operation
        O = n.Operation.INSIDE
        # O = n.Operation.OVERWRITE
        # Return node
        N = n.VoxelNode.Leaf(O, D)
        self.__node = N
        return N
