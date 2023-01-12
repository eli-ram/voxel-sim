from .parse import all as p
import glm

class Vector(p.Value[glm.vec3]):
    generic = glm.vec3

    def toString(self, value: glm.vec3) -> str:
        name = self.__class__.__name__
        x, y, z = value
        return f"{name}({x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f})"
