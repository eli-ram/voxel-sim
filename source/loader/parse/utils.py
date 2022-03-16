from typing import Any, Callable, Dict, Iterable, List, Tuple, Type, TypeVar
from typing_extensions import TypeGuard

from .error import CastError, ParseError
from .indent import Fmt
from .parsable import Parsable
import traceback

T = TypeVar('T')
P = TypeVar('P', bound=Parsable)
Parse = Callable[[P, Any], None]
Cast = Callable[[P, Any], T]


def _err(e: Exception) -> str:
    name = e.__class__.__name__
    args = ", ".join(e.args)
    return f"{name}[{args}]"


def _trace(e: Exception) -> str:
    _, *trace = traceback.format_tb(e.__traceback__, None)
    where = "\n" + "\n".join(trace)
    return where.replace('\n', '\n\t|')


def safeParse(method: Parse[P]):
    def safely(self: P, data: Any):
        try:
            self.error = False
            self.what = ""
            method(self, data)
        except ParseError as e:
            self.error = True
            self.what = _err(e)
        except Exception as e:
            self.error = True
            self.what = _err(e) + _trace(e)
    return safely


def wrapCast(method: Cast[P, T]):
    def wrapper(self: P, data: Any) -> T:
        try:
            return method(self, data)
        except Exception as e:
            raise CastError(*e.args)
    return wrapper


def linkParse(parent: Parsable, child: Parsable, data: Any):
    child.parse(data)
    parent.changed |= child.changed
    parent.error |= child.error


def isParsableType(cls: Any) -> TypeGuard[Type[Parsable]]:
    """ Check if Parsable or GenericParsable """
    if hasattr(cls, '__origin__'):
        cls = getattr(cls, '__origin__')
    return isinstance(cls, type) and issubclass(cls, Parsable)


def isMap(data: Any) -> TypeGuard[Dict[str, Any]]:
    return isinstance(data, dict)


def isArray(data: Any) -> TypeGuard[List[Any]]:
    return isinstance(data, list)


def formatIter(self: Parsable, F: Fmt, key: str, iter: Iterable[Tuple[Any, Parsable]]) -> str:
    """ Internal format method """
    N = F.next()
    K = F.format.list_unchanged
    E = F.format.list_errors

    def include(v: Parsable) -> bool:
        return (
            (E and v.error)
            or
            (K or v.changed)
        )

    S = {key.format(k): v.format(N) for k, v in iter if include(v)}
    if not S:
        return self.what

    I = F.indent()
    W = max(len(k) for k in S) + 1
    return self.what + "".join(I + k.ljust(W) + v for k, v in S.items())
