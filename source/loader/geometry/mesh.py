from ..parse import all as p
from .geometry import Geometry

class Mesh(Geometry, type='mesh'):
    file: p.String
