from typing import Any, Tuple, Dict, List, TypeVar
from .indent import Fmt
from .parsable import Parsable

def isParsableType(T: Any) -> bool:
    P = type(Parsable)
    I = isinstance
    return I(T, P) or I(getattr(T, '__origin__'), P)

def generics(obj: Any) -> Tuple[type, ...]:
    """ Get the Generic-Types of a Generic[T, ...] object """
    return obj.__orig_class__.__args__

def generic(obj: Any) -> type:
    """ Get the Generic-Type of a Generic[T] object """
    cls, = generics(obj)
    return cls

def _fmt(V: Dict[str, Parsable], F: Fmt) -> str:
    """ Internal format method """
    if not V:
        return str()
    W = max(len(k) for k in V) + 1
    N = F.next()
    I = F.indent()
    K = F.format.keep_unchanged
    return "".join(I + k.ljust(W) + v.format(N) for k, v in V.items() if K or v.changed)

P = TypeVar('P', bound=Parsable)

def formatMap(V: Dict[str, P], F: Fmt) -> str:
    return _fmt({f"{k}:": v for k, v in V.items()}, F)

def formatArray(V: List[P], F: Fmt) -> str:
    return _fmt({f"[{i}]:": v for i, v in enumerate(V)}, F)