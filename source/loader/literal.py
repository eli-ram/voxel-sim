from typing import Any, Dict, List, TypeVar
from .parse import Indent, ValueParsable, Formatter
import glm

T = TypeVar('T')

class Int(ValueParsable[int]):
    def validate(self, data: Any):
        return int(data)

class Float(ValueParsable[float]):
    def validate(self, data: Any):
        return float(data)

class String(ValueParsable[str]):
    def validate(self, data: Any):
        return str(data)

class Map(ValueParsable[Dict[str, T]]):
    def validate(self, data: Any):
        return data or {}

    def format(self, I: Indent) -> str:
        return Formatter.LiteralDict(self.value, I)

    def __getitem__(self, key: str):
        return self.value[key]

class Array(ValueParsable[List[T]]):
    def validate(self, data: Any):
        return data or []

    def format(self, I: Indent) -> str:
        return Formatter.LiteralList(self.value, I)

    def __getitem__(self, index: int):
        return self.value[index]

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
