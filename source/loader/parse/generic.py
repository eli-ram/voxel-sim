import typing as t
import inspect as i

T = t.TypeVar('T')

def value(method: t.Callable[[t.Any], T]) -> T:
    return property(method) # type: ignore

class Generic(t.Generic[T]):
    _generic: t.Optional[t.Type[T]] = None

    @value
    def generic(self) -> t.Type[T]:
        if not self._generic:
            self._generic = _generic(self)
        return self._generic

def _generic(obj: t.Generic[T]) -> t.Type[T]:
    origin = getattr(obj, '__orig_class__', None)
    if origin is None:
        name = obj.__class__.__name__
        file = i.getfile(obj.__class__)
        assert False, f"Cannot infer generic for class {name} (file: '{file}')"
    generic, = origin.__args__
    return generic
