from typing import Dict, Optional

from ..parse import all as p
from ..transform import Transform
from ..material import MaterialKey
from source.data import material as m
    
class Geometry(p.PolymorphicStruct):
    # Voxel operation
    operation: p.String

    # Voxel Material Key
    material: MaterialKey

    # Geometry Transform
    transform: Transform

    def loadMaterial(self, store: m.MaterialStore):
        self.material.load(store)



