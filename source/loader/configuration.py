from .parse import all as p
from .parameters import Parameters
from .geometry import Geometry
from .material import MaterialStore
from .box import Box


class Config(p.Struct):
    # Build Voxels
    build: p.Bool

    # Render Raw Geometry
    render: p.Bool

    # Constrain Voxel Region
    region: Box

    # Render Resolution per voxel
    resolution: p.Int


class Configuration(p.Struct):
    # General Settings
    config: Config

    # Defined Materials
    materials: MaterialStore
    
    # Application order of Geometry
    geometry: p.Array[p.Polymorphic[Geometry]]

    # Machine Learning Parameters
    parameters: Parameters

    def postParse(self):
        for child in self.geometry:
            child.require().loadMaterial(self.materials.get())
