from .parse.collection import Map, Array
from .parse.literal import Int
from .parse.struct import Struct
from .parameters import Parameters
from .geometry import Geometry
from .material import Material

class Config(Struct):
    size: Int
    resolution: Int

class Configuration(Struct):
    # General Settings
    config: Config

    # Defined Materials
    materials: Map[Material]

    # Application order of Geometry
    geometry: Array[Geometry]

    # Machine Learning Parameters
    parameters: Parameters
