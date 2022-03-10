from .transform import Transform
from .parse.struct import Struct
from .parse.literal import String
from .parse.collection import Map

class Geometry(Struct):
    type: String
    operation: String
    material: String
    transform: Transform
    properties: Map[String]
