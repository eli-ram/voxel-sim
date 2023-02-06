import glm
import numpy as np

import source.data.mesh as m
import source.math.utils as u
import source.utils.shapes as shp
import source.graphics.matrices as mat
import source.data.voxel_tree.node as n
import source.math.fields as f

from .geometry import Geometry, Context

field = f.Sphere()


class Sphere(Geometry, type='sphere-old'):
    """ A unit sphere """

    __node: n.VoxelNode

    def getMesh(self) -> m.Mesh:
        return shp.sphere()

    def buildVoxels(self, ctx: Context) -> n.VoxelNode:
        ctx, old = self._cacheCtx(ctx)

        changed = (
            not ctx.eq(old)
            or self.material.hasChanged()
            or self.operation.hasChanged()
        )

        # Compute if cache is busted
        if changed:
            # Compute
            O = self.operation.require()
            M = self.material.get()
            G = field.compute(ctx.shape, ctx.matrix, 1.0)
            D = n.Data.FromMaterialGrid(M, G)
            N = n.VoxelNode.Leaf(O, D)

            # Cache
            self.__node = N

        return self.__node


class Sphere2(Geometry, type='sphere'):
    """ A unit sphere """

    __node: n.VoxelNode

    def getMesh(self) -> m.Mesh:
        return shp.sphere_2(64)

    def buildVoxels(self, ctx: Context) -> n.VoxelNode:
        ctx, old = self._cacheCtx(ctx)

        changed = (
            not ctx.eq(old)
            or self.material.hasChanged()
            or self.operation.hasChanged()
        )

        # Compute if cache is busted
        if changed:
            # Compute
            O = self.operation.require()
            M = self.material.get()
            G = field.compute(ctx.shape, ctx.matrix, 1.0)
            D = n.Data.FromMaterialGrid(M, G)
            N = n.VoxelNode.Leaf(O, D)

            # Cache
            self.__node = N

        return self.__node
