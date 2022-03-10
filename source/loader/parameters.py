from .parse.struct import ParsableStruct
from .parse.literal import String, Float, Vector

class Surface(ParsableStruct):
    type: String
    radius: Float
    center: Vector
    normal: Vector

class Parameters(ParsableStruct):
   inner_surface: Surface
   outer_surface: Surface