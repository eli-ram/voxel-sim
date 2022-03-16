import typing as t
import inspect as i

T = t.TypeVar('T')

class Generic(t.Generic[T]):

    def generic(self) -> t.Type[T]:
        return get_generic(self)

def get_generic(obj: t.Generic[T]) -> t.Type[T]:
    origin = getattr(obj, '__orig_class__', None)
    if origin is None:
        name = obj.__class__.__name__
        file = i.getfile(obj.__class__)
        assert False, f"Cannot infer generic for {name}()! (file: {file})"
    generic, = origin.__args__
    return generic
