from .transform import Transform
from .parse import all as p

class Geometry(p.Struct):
    type: p.String
    operation: p.String
    material: p.String
    transform: Transform
    properties: p.Map[p.String]
