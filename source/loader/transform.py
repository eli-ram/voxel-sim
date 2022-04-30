from typing_extensions import TypeGuard
from typing import Any, Dict, List, Optional, TypeVar
from .parse import all as p
from .vector import Vector
import glm

T = TypeVar('T')
def _(v: Optional[T]) -> TypeGuard[T]:
    return v is not None

class Position(Vector):
    default = glm.vec3()


class Scale(Vector):
    default = glm.vec3(1, 1, 1)


class Rotation(p.Value[glm.quat]):

    def fromMap(self, data: Dict[str, Any]):
        angle = data['angle']
        axis = glm.vec3(data['axis'])
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

    matrix = glm.mat4()

    def postParse(self):
        # TODO: combine into a matrix
        M = glm.mat4()
        if _(pos := self.position.get()):
            M *= glm.translate(pos)
        if _(rot := self.rotation.get()):
            rot = glm.normalize(rot)
            M *= glm.mat4_cast(rot)
        if _(scale := self.scale.get()):
            M *= glm.scale(scale)
        self.matrix = M
        print(f'transform:\n{M}')