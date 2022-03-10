from .transform import Transform
from .parse.literal import String, Map
from .parse.auto import AutoParsable
from .parse.parse import ListParsable

class Geometry(AutoParsable):
    type: String
    operation: String
    material: String
    transform: Transform
    properties: Map[str]

class GeometryList(ListParsable[Geometry]):
    child = Geometry