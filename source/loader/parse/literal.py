from typing import Any
from .indent import Indent
from .value import ValueParsable
from .error import ParseError
import glm

class Int(ValueParsable[int]):
    def validate(self, data: Any):
        if not isinstance(data, int):
            raise ParseError("Expected an Integer")
        return data

class Float(ValueParsable[float]):
    def validate(self, data: Any):
        if not isinstance(data, (int, float)):
            raise ParseError("Expected a Float")
        return float(data)

class String(ValueParsable[str]):
    def validate(self, data: Any):
        if not isinstance(data, str):
            raise ParseError("Expected a String")
        return data


class Vector(ValueParsable[glm.vec3]):
    default = glm.vec3()

    def validate(self, data: Any):
        if isinstance(data, (float, int)):
            return glm.vec3(data, data, data)
        if isinstance(data, list):
            return glm.vec3(*data)
        else:
            return self.default

    def format(self, I: Indent) -> str:
        x, y, z = self.value
        return f"Vector({x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f})"

class Quaternion(ValueParsable[glm.quat]):
    def validate(self, data: Any):
        # TODO
        return glm.quat()

    def format(self, I: Indent) -> str:
        w, x, y, z = self.value
        return f"Quaternion({w=: 6.3f}, {x=: 6.3f}, {y=: 6.3f}, {z=: 6.3f})"
