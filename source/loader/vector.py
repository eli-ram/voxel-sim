from typing import Any
from .parse import all as p
import glm

class Vector(p.Value[glm.vec3]):
    default: glm.vec3
    
    def validate(self, data: Any):
        if isinstance(data, (float, int)):
            return glm.vec3(data, data, data)
        if isinstance(data, list):
            return glm.vec3(*data)
        else:
            return self.default

    def string(self, value: glm.vec3) -> str:
        name = type(self).__name__
        x, y, z = value
        return f"{name}({x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f})"
