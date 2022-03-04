from .transform import Transform
from .literal import String, Data
from .parse import AutoParsable

class Geometry(AutoParsable):
    type: String
    operation: String
    transform: Transform
    properties: Data
