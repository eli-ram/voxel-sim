from typing import Any, Dict, List, TypeVar, cast
from .parse import Indent, ValueParsable, Fmt
from .error import ParseError
from .utils import generic
import glm

T = TypeVar('T')

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

class Map(ValueParsable[Dict[str, T]]):

    def validate(self, data: Any):
        data = data or {}

        if not isinstance(data, dict):
            raise ParseError("Expected a Map")

        map = cast(Dict[str, Any], data)
        cls = generic(self)
        if not all(isinstance(value, cls) for value in map.values()):
            raise ParseError(f"Expected a Map of {cls.__name__}")

        return map

    def format(self, I: Indent) -> str:
        return Fmt.LiteralDict(self.value, I)

    def __getitem__(self, key: str):
        return self.value[key]

class Array(ValueParsable[List[T]]):
    def validate(self, data: Any):
        data = data or []

        if not isinstance(data, list):
            raise ParseError("Expected an Array")

        arr = cast(List[Any], data)
        cls = generic(self)
        if not all(isinstance(value, cls) for value in arr):
            raise ParseError(f"Expected an Array of {cls.__name__}")
        
        return arr

    def format(self, I: Indent) -> str:
        return Fmt.LiteralList(self.value, I)

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
