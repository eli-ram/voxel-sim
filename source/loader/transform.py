from typing import Any, Dict, List, cast
from .parse import all as p
from .vector import Vector
import glm


class Position(Vector):
    default = glm.vec3()


class Scale(Vector):
    default = glm.vec3(1, 1, 1)


class Rotation(p.Value[glm.quat]):
    def validate(self, data: Any):
        # Use identity if missing
        if data is None:
            return glm.quat()

        # Support raw-quaternion
        if isinstance(data, list):
            quat = cast(List[Any], data)
            return glm.quat(*quat)

        if not isinstance(data, dict):
            raise p.CastError("Expected a Map or an Array")

        kwargs = cast(Dict[str, Any], data)
        angle = kwargs['angle']
        axis = glm.vec3(*kwargs['axis'])
        return glm.angleAxis(angle, axis)

    def string(self, value: glm.quat) -> str:
        name = type(self).__name__
        w, x, y, z = value
        return f"{name}({w=: 6.3f}, {x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f})"


class Transform(p.Struct):
    rotation: Rotation
    position: Position
    scale: Scale
