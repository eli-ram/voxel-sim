from .parse.struct import Struct
from .parse.literal import String, Float, Vector

class Surface(Struct):
    type: String
    radius: Float
    center: Vector
    normal: Vector

class Parameters(Struct):
   inner_surface: Surface
   outer_surface: Surface