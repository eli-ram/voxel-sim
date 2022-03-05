from .parse import AutoParsable
from .literal import String, Float, Vector

class Surface(AutoParsable):
    type: String
    radius: Float
    center: Vector
    normal: Vector

class Parameters(AutoParsable):
   inner_surface: Surface
   outer_surface: Surface