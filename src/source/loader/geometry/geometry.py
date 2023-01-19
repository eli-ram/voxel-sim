from traceback import print_exc

from source.utils.wireframe.wireframe import Wireframe
from source.data.voxel_tree import (
    box, data, node, operation
)
from source.interactive import (
    scene as s,
)
from source.data import (
    material as m,
    mesh,
)

from ..parse import all as p
from ..transform import TransformArray
from ..material import MaterialKey


def void_on_error(method):
    def wrap(self: 'Geometry', *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except:
            print_exc()
            return s.Void()
    return wrap


class Geometry(p.PolymorphicStruct):
    # Voxel operation
    operation: p.String

    # Voxel Material Key
    material: MaterialKey

    # Geometry Transform
    transform: TransformArray

    def loadMaterial(self, store: m.MaterialStore):
        self.setError(self.material.load(store))

    def getMesh(self) -> mesh.Mesh:
        raise NotImplementedError()

    @void_on_error
    def getRender(self) -> s.Render:
        # Render a Wireframe
        mesh = self.getMesh()
        color = self.material.get().color
        matrix = self.transform.matrix
        model = Wireframe(mesh).setColor(color)
        return s.Transform(matrix, model)

    def getVoxelNode(self) -> node.VoxelNode:
        raise NotImplementedError()


_G = p.Polymorphic[Geometry]
class GeometryArray(p.Array[_G]):
    """ A Sequenced Array of Geometry """
    generic = _G

    def __iter__(self):
        for child in self._array:
            geometry = child.get()
            if geometry is None:
                continue
            if geometry.hasError():
                continue
            yield geometry

    def loadMaterials(self, store: m.MaterialStore):
        for child in self:
            child.loadMaterial(store)

    def getRenders(self):
        return [child.getRender() for child in self]
