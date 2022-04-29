from source.data import mesh
from source.utils.shapes import origin_marker
from .geometry import Geometry

class Sphere(Geometry, type='sphere'):
    """ A unit sphere """

    def getMesh(self) -> mesh.Mesh:
        ## TODO: make sphere...
        return origin_marker()
