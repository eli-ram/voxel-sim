from ..parse import all as p
from .geometry import Geometry
from source.interactive import (
    scene as s,
)

class Composite(Geometry, type='composite'):
    """ Compose Geometry from child instances """

    # There is no material for a composition
    material: None

    # The list of children
    children: p.Array[p.Polymorphic[Geometry]]

    def __iter__(self):
        for child in self.children:
            if geometry := child.get():
                yield geometry

    def loadMaterial(self, store):
        for child in self:
            child.loadMaterial(store)

    def getRender(self) -> s.Render:
        matrix = self.transform.matrix
        children = [c.getRender() for c in self]
        return s.Scene(matrix, children)

