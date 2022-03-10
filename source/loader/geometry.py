from .transform import Transform
from .parse.struct import ParsableStruct
from .parse.literal import String
from .parse.collection import ParsableMap

class Geometry(ParsableStruct):
    type: String
    operation: String
    material: String
    transform: Transform
    properties: ParsableMap[String]
