from source.parser import all as p
import glm


class Vec2(p.Value[glm.vec2]):
    generic = glm.vec2

    def toString(self, value: glm.vec2) -> str:
        name = self.__class__.__name__
        x, y = value
        return f"{name}({x=: 6.3f}, {y=: 6.3f})"


class Vec3(p.Value[glm.vec3]):
    generic = glm.vec3

    def toString(self, value: glm.vec3) -> str:
        name = self.__class__.__name__
        x, y, z = value
        return f"{name}({x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f})"


class Vec4(p.Value[glm.vec4]):
    generic = glm.vec4

    def toString(self, value: glm.vec4) -> str:
        name = self.__class__.__name__
        x, y, z, w = value
        return f"{name}({x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f}, {w=: 6.3f})"
