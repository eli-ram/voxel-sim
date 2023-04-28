from typing import Callable, TypeVar, Generic

C = TypeVar('C')
T = TypeVar('T')


def cache(method: Callable[[C], T]) -> Callable[[C], T]:
    K = f"__{method.__name__}"
    def wrap(self: C) -> T:
        if not hasattr(self, K):
            setattr(self, K, method(self))
        return getattr(self, K)
    return wrap

class Attr(Generic[T]):
    def opt(self) -> T | None:
        return getattr(self, '__value', None)

    def has(self) -> bool:
        return hasattr(self, '__value')

    def get(self) -> T:
        return getattr(self, '__value')

    def set(self, value: T):
        setattr(self, '__value', value)
        return value

def _is_attr(cls):
    if hasattr(cls, '__origin__'):
        cls = getattr(cls, '__origin__')
    return isinstance(cls, type) and issubclass(cls, Attr)

class Cache:
    def __init__(self):
        fields = self.__annotations__
        for name, field in fields.items():
            if _is_attr(field):
                setattr(self, name, field())

class Lazy(Generic[T]):

    def __init__(self, fn: Callable[[], T]):
        self.__fn = fn

    def get(self) -> T:
        if not hasattr(self, '__value'):
            setattr(self, '__value', self.__fn())
        return getattr(self, '__value')

