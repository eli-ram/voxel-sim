from typing import Any, Callable, Tuple, Dict, List, TypeVar

from .error import ParseError, CastError
from .indent import Fmt
from .parsable import Parsable

P = TypeVar('P', bound=Parsable)
Parse = Callable[[P, Any], None]

def safeParse(method: Parse[P]):
    def safely(self: Parsable, data: Any):
        try:
            self.error = None
            method(self, data)
        except ParseError as e:
            self.error = e
        except Exception as e:
            self.error = CastError(",".join(e.args))
    return safely

def isParsableType(cls: Any) -> bool:
    """ Check if Parsable or GenericParsable """
    cls = cls if isinstance(cls, type) else getattr(cls, '__origin__')
    return issubclass(cls, Parsable)

def generics(obj: Any) -> Tuple[type, ...]:
    """ Get the Generic-Types of a Generic[T, ...] object """
    return obj.__orig_class__.__args__

def generic(obj: Any) -> type:
    """ Get the Generic-Type of a Generic[T] object """
    cls, = generics(obj)
    return cls

def _fmt(self: Parsable, V: Dict[str, Parsable], F: Fmt) -> str:
    """ Internal format method """
    if not V:
        return str()

    W = max(len(k) for k in V) + 1
    N = F.next()
    I = F.indent()
    K = F.format.list_unchanged
    E = F.format.list_errors

    def include(v: Parsable) -> bool:
        return (
            (E and not v.error is None)
            or
            (K or v.changed)
        )

    if E and self.error:
        base = str(self.error)
    else:
        base = str()
        
    return base + "".join(I + k.ljust(W) + v.format(N) for k, v in V.items() if include(v))

def formatValue(self: Parsable, V: str, F: Fmt) -> str:
    E = F.format.list_errors
    if E and self.error:
        return str(self.error)
    
    return V

def formatMap(self: Parsable, V: Dict[str, P], F: Fmt) -> str:
    return _fmt(self, {f"{k}:": v for k, v in V.items()}, F)

def formatArray(self: Parsable, V: List[P], F: Fmt) -> str:
    return _fmt(self, {f"[{i}]:": v for i, v in enumerate(V)}, F)