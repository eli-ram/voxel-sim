from .parse.auto import AutoParsable
from .parse.literal import Vector, Quaternion
import glm

class Scale(Vector):
    default = glm.vec3(1, 1, 1)

class Transform(AutoParsable):
    rotation: Quaternion
    position: Vector
    scale: Scale
