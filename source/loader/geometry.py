from .transform import Transform
from .parse import all as p

class Geometry(p.PolymorphicStruct):
    operation: p.String
    material: p.String
    transform: Transform

class Mesh(Geometry, type='mesh'):
    file: p.String

class Sphere(Geometry, type='sphere'):
    pass