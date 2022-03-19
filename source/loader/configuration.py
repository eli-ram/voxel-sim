from .parse import all as p
from .parameters import Parameters
from .geometry import Geometry
from .material import Material

class Config(p.Struct):
    size: p.Int
    build: p.Bool
    render: p.Bool
    resolution: p.Int

class Configuration(p.Struct):
    # General Settings
    config: Config

    # Defined Materials
    materials: p.Map[Material]

    # Application order of Geometry
    geometry: p.Array[p.Polymorphic[Geometry]]

    # Machine Learning Parameters
    parameters: Parameters
