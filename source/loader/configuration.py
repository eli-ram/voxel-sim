from .parse import AutoParsable
from .parameters import Parameters
from .geometry import GeometryList
from .literal import Int
from .material import ColorMap

class Config(AutoParsable):
    size: Int
    resolution: Int

class Configuration(AutoParsable):
    config: Config
    colors: ColorMap
    geometry: GeometryList
    parameters: Parameters
