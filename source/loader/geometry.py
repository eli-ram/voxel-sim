from .transform import Transform
from .literal import String, Map
from .parse import AutoParsable, ListParsable

class Geometry(AutoParsable):
    type: String
    operation: String
    material: String
    transform: Transform
    properties: Map[str]

class GeometryList(ListParsable[Geometry]):
    child = Geometry