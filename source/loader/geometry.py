from .transform import Transform
from .literal import String, Data
from .parse import AutoParsable, ListParsable

class Geometry(AutoParsable):
    type: String
    operation: String
    transform: Transform
    properties: Data

class GeometryList(ListParsable[Geometry]):
    def create(self):
        return Geometry()
