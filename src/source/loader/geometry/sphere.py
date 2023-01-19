from source.data import mesh
from source.utils.shapes import sphere, sphere_2
from .geometry import Geometry

class Sphere(Geometry, type='sphere'):
    """ A unit sphere """

    def getMesh(self) -> mesh.Mesh:
        return sphere()

class Sphere2(Geometry, type='sphere-2'):
    """ A unit sphere """

    def getMesh(self) -> mesh.Mesh:
        return sphere_2(64)
