from .parse import all as p
from .parameters import Parameters
from .geometry import GeometryArray
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
    geometry: GeometryArray
    
    # Machine Learning Parameters
    parameters: Parameters

    def postParse(self):
        store = self.materials.get()
        self.geometry.loadMaterials(store)

    def getRender(self) -> s.Render:
        children = self.geometry.getRenders()
        return s.Scene(children=children)

