import os
import numpy as np

import source.graphics.matrices as mat
import source.data.voxel_tree.node as n
import source.parser.all as p
import source.data.mesh as m

from source.math.mesh2voxels import mesh_to_voxels
from source.utils.mesh_loader import cacheMesh

from .geometry import Context, Geometry


class Mesh(Geometry, type='mesh'):
    file: p.String
    __mesh: m.Mesh
    __node: n.VoxelNode

    def postParse(self):
        file = self.file.require()
        file = os.path.abspath(file)

        try:
            # Get or Load mesh
            self.__mesh = cacheMesh(file)
        except FileNotFoundError:
            raise p.ParseError(f"File Not Found: \"{file}\"")

    def getMesh(self) -> m.Mesh:
        return self.__mesh

    def getVoxels(self, ctx: Context) -> n.VoxelNode:
        # Cache context
        ctx, old = self._cacheCtx(ctx)

        changed = (
            not ctx.eq(old)
            or self.file.hasChanged()
            or self.operation.hasChanged()
            or self.material.hasChanged()
        )

        # Check if cached value is valid
        if not changed:
            return self.__node

        # Compute voxels (TODO: remove offset calc ...)
        offset, grid = mesh_to_voxels(
            # Cached mesh
            self.__mesh,
            # Transformation
            mat.to_affine(ctx.matrix),
            # relevant area
            ctx.shape
        )
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
        O = self.operation.require()
        # Return node
        N = n.VoxelNode.Leaf(O, D)
        self.__node = N
        return N
