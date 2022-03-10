from typing import Any, Tuple
from .parsable import Parsable

def isParsableType(T: Any) -> bool:
    P = type(Parsable)
    I = isinstance
    return I(T, P) or I(getattr(T, '__origin__'), P)

def generics(obj: Any) -> Tuple[type, ...]:
    return obj.__orig_class__.__args__

def generic(obj: Any) -> type:
    cls, = generics(obj)
    return cls

