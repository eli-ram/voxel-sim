import os
from traceback import print_exc

import numpy as np

import source.graphics.matrices as mat
import source.data.voxel_tree.node as n
import source.parser.all as p
import source.data.mesh as m
import source.math.mesh2voxels as m2v

from source.utils.mesh_loader import cacheMesh

from .geometry import Context, Geometry


class Mesh(Geometry, type='mesh'):
    file: p.String
    mesh: m.Mesh

    def postParse(self):
        file = self.file.require()
        file = os.path.abspath(file)

        try:
            self.mesh = cacheMesh(file)
        except FileNotFoundError:
            raise p.ParseError(f"File Not Found: \"{file}\"")

    def getMesh(self) -> m.Mesh:
        return self.mesh

    def getVoxels(self, ctx: Context) -> n.VoxelNode:
        # Build transform
        T = mat.to_affine(
            # Local transform
            self.transform.matrix
        )
        # Compute shape
        S = ctx.box.shape
        # Compute voxels
        offset, grid = m2v.mesh_to_voxels(self.mesh, T, S)
        # Get material
        M = self.material.get()
        # Package Data
        D = n.Data(
            box=n.Box.OffsetShape(offset, grid.shape),
            mask=grid,
            material=(grid * M.id).astype(np.uint32),
            strength=(grid * M.strength).astype(np.float32),
        )
        # Get operation
        O = n.Operation.OVERWRITE
        # Return node
        return n.VoxelNode.Leaf(O, D)
