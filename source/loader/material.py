from typing import Any, Dict, List, NamedTuple
from .parse import all as p
from .vector import Vector
from source.data import (
    colors,
    material as m,
)

class Locks(NamedTuple):
    x: bool = False
    y: bool = False
    z: bool = False

class Color(p.Value[colors.Color]):
    def fromNone(self):
        return colors.get.WHITE

    def fromMap(self, data: Dict[str, Any]):
        return colors.Color(**data)

    def fromArray(self, data: List[Any]):
        return colors.Color(*data)

    def fromValue(self, data: Any):
        return colors.get(data)
        
class Material(p.Struct):
    color: Color
    strength: p.Float
    locks: p.Value[Locks]
    force: Vector

class MaterialStore(p.Map[Material]):
    generic = Material
    _cache: m.MaterialStore

    def post_validate(self):
        store = m.MaterialStore()
        for key, value in self:
            store.create(key, value.color.require())
        self._cache = store

    def get(self):
        return self._cache

class MaterialKey(p.String):
    _cache: m.Material

    def load(self, store: m.MaterialStore):
        key = self._value

        if key is None:
            raise p.ParseError("Missing material key!")

        if key not in store:
            err = f"Material does not exist! (key: {key})"
            raise p.ParseError(err)

        self._cache = store[key]

    def get(self):
        return self._cache
