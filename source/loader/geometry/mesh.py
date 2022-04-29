from ..parse import all as p
from .geometry import Geometry
from source.data import mesh as m
from source.utils.mesh_loader import cacheMesh

class Mesh(Geometry, type='mesh'):
    file: p.String
    mesh: m.Mesh

    def postParse(self):
        file = self.file.require()
        self.mesh = cacheMesh(file)
        
    def getMesh(self) -> m.Mesh:
        if not hasattr(self, 'mesh'):
            raise NotImplementedError("Validation Error...")
        return self.mesh
