from .transform import Transform
from .parse.auto import AutoParsable
from .parse.literal import String
from .parse.collection import ParsableMap

class Geometry(AutoParsable):
    type: String
    operation: String
    material: String
    transform: Transform
    properties: ParsableMap[String]
