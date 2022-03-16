from typing import Any, Dict, List
from .parse import all as p
from .vector import Vector
import glm


class Position(Vector):
    default = glm.vec3()


class Scale(Vector):
    default = glm.vec3(1, 1, 1)


class Rotation(p.Value[glm.quat]):

    def fromMap(self, data: Dict[str, Any]):
        angle = data['angle']
        axis = glm.vec3(*data['axis'])
        return glm.angleAxis(angle, axis)

    def fromArray(self, data: List[Any]):
        return glm.quat(*data)

    def fromValue(self, data: Any):
        raise p.CastError("Expected a Map or an Array")

    def toString(self, value: glm.quat) -> str:
        name = self.__class__.__name__
        w, x, y, z = value
        return f"{name}({w=: 6.3f}, {x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f})"


class Transform(p.Struct):
    rotation: Rotation
    position: Position
    scale: Scale

    def validate(self):
        # TODO: combine into a matrix
        print("Transform:")
        if self.rotation:
            print(" - Has", self.rotation)
        if self.position:
            print(" - Has", self.position)
        if self.scale:
            print(" - Has", self.scale)
        print()