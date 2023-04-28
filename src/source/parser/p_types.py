from typing import List, Dict, Any, Union
from typing_extensions import TypeGuard


def isMap(data: Any) -> TypeGuard['Map']:
    return isinstance(data, dict)


def isArray(data: Any) -> TypeGuard['Array']:
    return isinstance(data, list)


def getAnnotations(cls: Union[object, type]):
    # Get class if object
    cls = cls if isinstance(cls, type) else cls.__class__
    # Construct return type
    annotations = dict[str, Any]()
    # Reverse throught class hierarchy
    for C in reversed(cls.mro()):
        # Extract annotations (last is top type)
        if hasattr(C, '__annotations__'):
            annotations.update(C.__annotations__)
    # Annotations now reflect class hierarchy (including overloaded attributes)
    return annotations


Any = Any
Map = Dict[str, Any]
Array = List[Any]
