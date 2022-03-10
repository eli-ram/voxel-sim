from .parse.struct import Struct
from .parse.literal import Vector, Quaternion
import glm

class Scale(Vector):
    default = glm.vec3(1, 1, 1)

class Transform(Struct):
    rotation: Quaternion
    position: Vector
    scale: Scale
