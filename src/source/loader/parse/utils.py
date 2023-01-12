from typing import Callable, Iterable, Tuple, Type, TypeVar
from typing_extensions import TypeGuard

from .types import Any, Map
from .error import CastError
from .indent import Fmt
from .parsable import Parsable

T = TypeVar('T')
P = TypeVar('P', bound=Parsable)
Cast = Callable[[P, Any], T]

def wrapCast(method: Cast[P, T]):
    def wrapper(self: P, data: Any) -> T:
        try:
            return method(self, data)
        except Exception as e:
            raise CastError(*e.args)
    return wrapper


def annotations(cls: type) -> Map:
    """ Get all the annotations on a class """
    all = dict[str, Any]()
    for C in reversed(cls.mro()):
        if hasattr(C, '__annotations__'):
            all.update(C.__annotations__)
    return all


def isParsableType(cls: Any) -> TypeGuard[Type[Parsable]]:
    """ Check if Parsable or GenericParsable """
    if hasattr(cls, '__origin__'):
        cls = getattr(cls, '__origin__')
    return isinstance(cls, type) and issubclass(cls, Parsable)


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
