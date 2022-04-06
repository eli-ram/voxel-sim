from ..parse import all as p
from .geometry import Geometry

class Composite(Geometry, type='composite'):
    """ Compose Geometry from child instances """

    # There is no material for a composition
    material: None

    # The list of children
    children: p.Array[p.Polymorphic[Geometry]]

    def loadMaterial(self, store):
        for child in self.children:
            child.require().loadMaterial(store)
