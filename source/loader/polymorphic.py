from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from .parse import Params, Parsable


class Typed(Parsable):
    TYPE: str


T = TypeVar('T', bound=Typed)


class PolymophicParser(Generic[T]):
    TYPES: List[Type[T]]

    def __init__(self):
        self._map = {t.TYPE: t for t in self.TYPES}

    def parse(self, data: Params, instance: Optional[T]) -> Optional[T]:
        type = (data or {}).get("type")
        if type is None:
            return
        if type is not getattr(instance, "TYPE"):
            instance = self._map[type]()
        instance.parse(data)
        return instance            