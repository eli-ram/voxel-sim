from .parse.struct import ParsableStruct
from .parse.literal import Vector, Quaternion
import glm

class Scale(Vector):
    default = glm.vec3(1, 1, 1)

class Transform(ParsableStruct):
    rotation: Quaternion
    position: Vector
    scale: Scale
