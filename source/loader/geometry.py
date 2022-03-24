from typing import Dict, Optional
from .transform import Transform
from .material import Material
from .parse import all as p

Materials = Dict[str, Material]

class Cache:
    material: Optional[Material] = None
    
class Geometry(p.PolymorphicStruct):
    operation: p.String
    material: p.String
    transform: Transform

    def __init__(self) -> None:
        super().__init__()
        self.cache = Cache()

    def checkMaterials(self, materials: Materials):
        if key := self.material.value: 
            self.cache.material = materials[key]
        else:
            self.cache.material = None

    def logMaterials(self, I: str):
        key = self.material.value
        if mat := self.cache.material:
            color = mat.color.value
        else:
            color = None
        print(f"{I} {key} => {color}")

class GeometryArray(Geometry, type='array'):
    material: None
    children: p.Array[p.Polymorphic[Geometry]]

    def checkMaterials(self, materials: Materials):
        super().checkMaterials(materials)
        for child in self.children:
            child.require().checkMaterials(materials)

    def logMaterials(self, I: str):
        super().logMaterials(I)
        N = I + "  "
        for child in self.children:
            child.require().logMaterials(N)

class Mesh(Geometry, type='mesh'):
    file: p.String

class Sphere(Geometry, type='sphere'):
    pass