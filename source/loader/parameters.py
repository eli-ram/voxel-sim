from .parse.struct import Struct
from .parse.literal import String
from .transform import Transform

class Surface(Struct):
    type: String
    transform: Transform

class Parameters(Struct):
   inner_surface: Surface
   outer_surface: Surface