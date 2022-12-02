from typing import Any, Dict, TypeVar
from .indent import Fmt
from .parsable import Parsable
from .generic import Generic
from .error import ParseError
from . import p_types, utils

P = TypeVar('P', bound=Parsable)


class Map(Parsable, Generic[P]):
    _map: Dict[str, P]

    def __init__(self) -> None:
        self._map = {}

    def dataParse(self, data: Any):
        data = data or {}

        if not p_types.isMap(data):
            raise ParseError("Expected a Map")

        T = Generic.get(self)
        V = set(self._map)
        D = set(data)

        # Baseline for change
        self.changed = D != V

        # Create
        for key in D - V:
            self._map[key] = T()

        # Delete
        for key in V - D:
            self._map.pop(key)

        # Parse & Check changes / errors
        for key, parsable in self._map.items():
            yield parsable, data.get(key)

    def formatValue(self, F: Fmt) -> str:
        return utils.formatIter(self, F, "[{}]:", self._map.items())

    def __iter__(self):
        return iter(self._map.items())

    def __getitem__(self, key: str) -> P:
        return self._map[key]
