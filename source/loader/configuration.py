from .parse.auto import AutoParsable
from .parameters import Parameters
from .geometry import GeometryList
from .parse.literal import Int
from .material import MaterialMap

class Config(AutoParsable):
    size: Int
    resolution: Int

class Configuration(AutoParsable):
    # General Settings
    config: Config

    # Defined Materials
    materials: MaterialMap

    # Application order of Geometry
    geometry: GeometryList

    # Machine Learning Parameters
    parameters: Parameters
