import os
from traceback import print_exc

from source.data.voxel_tree import node
from source.parser import all as p
from .geometry import Geometry
from source.data import mesh as m
from source.utils.mesh_loader import cacheMesh

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

    def getVoxelNode(self) -> node.VoxelNode:
        return super().getVoxelNode()