from typing_extensions import TypeGuard
from typing import Any, Dict, List, Optional, TypeVar
from .parse import all as p
from .vector import Vector
from source.data.transform import Transform as _Transform
import glm

T = TypeVar('T')
def _(v: Optional[T]) -> TypeGuard[T]:
    return v is not None

class Position(Vector):
    
    @property
    def value(self):
        D = glm.vec3()
        return self.getOr(D)


class Scale(Vector):

    @property
    def value(self):
        D = glm.vec3(1, 1, 1)
        return self.getOr(D)

class Rotation(p.Value[glm.quat]):

    @property
    def value(self):
        D = glm.quat()
        return self.getOr(D)

    def fromMap(self, data: Dict[str, Any]):
        # Todo: euler
        angle = data['angle']
        axis = glm.vec3(data['axis'])
        return glm.angleAxis(angle, axis)

    def fromArray(self, data: List[Any]):
        quat = glm.quat(*data)
        return glm.normalize(quat)

    def fromValue(self, data: Any):
        raise p.CastError("Expected a Map or an Array")

    def toString(self, value: glm.quat) -> str:
        name = self.__class__.__name__
        w, x, y, z = value
        return f"{name}({w=: 6.3f}, {x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f})"


class Transform(p.Struct):
    scale: Scale
    rotation: Rotation
    position: Position

    matrix = glm.mat4()
    transform = _Transform()

    def postParse(self):
        T = self.transform
        T.scale = self.scale.value
        T.rotation = self.rotation.value
        T.position = self.position.value
        T.invalidate()
        self.matrix = self.transform.matrix

class TransformArray(p.Array[Transform]):
    generic = Transform
    matrix = glm.mat4()

    def postParse(self):
        P = None
        for t in self:
            T = t.transform
            T.parent = P
            P = T
        self.matrix = P.local_to_world if P else glm.mat4()
        print(f'transform:\n{self.matrix}')
