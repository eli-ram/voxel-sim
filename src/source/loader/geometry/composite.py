from .geometry import Geometry, GeometryArray
from source.interactive import (
    scene as s,
)

class Composite(Geometry, type='composite'):
    """ Compose Geometry from child instances """

    # There is no material for a composition
    material: None

    # The list of children
    children: GeometryArray
    
    def loadMaterial(self, store):
        self.children.loadMaterials(store)

    def getRender(self) -> s.Render:
        matrix = self.transform.matrix
        children = self.children.getRenders()
        return s.Scene(matrix, children)

