from .parse.collection import ParsableMap, ParsableArray
from .parse.literal import Int
from .parse.struct import ParsableStruct
from .parameters import Parameters
from .geometry import Geometry
from .material import Material

class Config(ParsableStruct):
    size: Int
    resolution: Int

class Configuration(ParsableStruct):
    # General Settings
    config: Config

    # Defined Materials
    materials: ParsableMap[Material]

    # Application order of Geometry
    geometry: ParsableArray[Geometry]

    # Machine Learning Parameters
    parameters: Parameters
