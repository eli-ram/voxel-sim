from typing import Any, Callable, Tuple, Dict, List, TypeVar
from .indent import Fmt
from .parsable import Parsable
import traceback

P = TypeVar('P', bound=Parsable)
Parse = Callable[[P, Any], None]

def _err(e: Exception) -> str:
    _, *trace = traceback.format_tb(e.__traceback__, None)
    where = "\n".join(trace)
    name = e.__class__.__name__
    return f"{name}[{e}]\n{where}".replace('\n','\n\t|')

def safeParse(method: Parse[P]):
    def safely(self: Parsable, data: Any):
        try:
            self.error = False
            self.what = ""
            method(self, data)
        except Exception as e:
            self.error = True
            self.what = _err(e)
    return safely

def linkParse(parent: Parsable, child: Parsable, data: Any):
    child.parse(data)
    parent.changed |= child.changed
    parent.error |= child.error

def isParsableType(cls: Any) -> bool:
    """ Check if Parsable or GenericParsable """
    if hasattr(cls, '__origin__'):
        cls = getattr(cls, '__origin__')
    return isinstance(cls, type) and issubclass(cls, Parsable)

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
            (E and v.error)
            or
            (K or v.changed)
        )
        
    return self.what + "".join(I + k.ljust(W) + v.format(N) for k, v in V.items() if include(v))

def formatMap(self: Parsable, V: Dict[str, P], F: Fmt) -> str:
    return _fmt(self, {f"[{k}]:": v for k, v in V.items()}, F)

def formatArray(self: Parsable, V: List[P], F: Fmt) -> str:
    return _fmt(self, {f"[{i}]:": v for i, v in enumerate(V)}, F)

def formatStruct(self: Parsable, V: Dict[str, P], F: Fmt) -> str:
    return _fmt(self, {f"{k}:": v for k, v in V.items()}, F)
