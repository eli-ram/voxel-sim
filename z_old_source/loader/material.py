from typing import Any, Dict, List, NamedTuple

from .parse import all as p
from .vector import Vec3
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
    force: Vec3


class MaterialStore(p.Map[Material]):
    generic = Material
    _cache: m.MaterialStore

    def postParse(self):
        store = m.MaterialStore()
        for key, value in self:
            store.create(key, value.color.require())
        self._cache = store

    def get(self):
        return self._cache


class MaterialKey(p.String):
    _cache: m.Material

    def load(self, store: m.MaterialStore):
        """ Load the material from the store """
        with self.captureErrors():
            key = self._value

            if key is None:
                raise p.ParseError("Missing material key!")

            if key not in store:
                raise p.ParseError(f"Material does not exist! (key: {key})")

            self._cache = store[key]

        return self.__error

    def get(self):
        """ Get the cached material """
        return self._cache
