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
from ..transform import Transform
from ..material import MaterialKey
    
def void_on_error(method):
    def wrap(self: 'Geometry', *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except:
            name = self.__class__.__name__
            print(f"[{name}] Voided Render!")
            print_exc()
            return s.Void()
    return wrap

class Geometry(p.PolymorphicStruct):
    # Voxel operation
    operation: p.String

    # Voxel Material Key
    material: MaterialKey

    # Geometry Transform
    transform: Transform

    def loadMaterial(self, store: m.MaterialStore):
        self.material.load(store)
        self.error |= self.material.error

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

