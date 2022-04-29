from .parse import all as p
from .parameters import Parameters
from .geometry import Geometry
from .material import Color, MaterialStore
from .box import Box

from source.interactive import scene as s


class Config(p.Struct):
    # Build Voxels
    build: p.Bool

    # Render Raw Geometry
    render: p.Bool

    # Constrain Voxel Region
    region: Box

    # Render Resolution per voxel
    resolution: p.Int

    # Background color
    background: Color


class Configuration(p.Struct):
    # General Settings
    config: Config

    # Defined Materials
    materials: MaterialStore
    
    # Application order of Geometry
    geometry: p.Array[p.Polymorphic[Geometry]]

    # Machine Learning Parameters
    parameters: Parameters

    def __iter__(self):
        for child in self.geometry:
            geometry = child.get()
            if geometry is None:
                continue
            if geometry.error:
                continue
            yield geometry

    def postParse(self):
        store = self.materials.get()
        for child in self:
            child.loadMaterial(store)

    def getRender(self) -> s.Render:
        children = [c.getRender() for c in self]
        return s.Scene(children=children)

