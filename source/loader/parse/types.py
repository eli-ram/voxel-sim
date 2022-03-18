from typing import List, Dict, Any
from typing_extensions import TypeGuard

Any = Any
Map = Dict[str, Any]
Array = List[Any]


def isMap(data: Any) -> TypeGuard[Map]:
    return isinstance(data, dict)


def isArray(data: Any) -> TypeGuard[Array]:
    return isinstance(data, list)
