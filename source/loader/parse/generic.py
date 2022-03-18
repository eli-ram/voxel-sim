import typing as t
import inspect as i

T = t.TypeVar('T')

def value(method: t.Callable[[t.Any], T]) -> T:
    return property(method) # type: ignore

class InferenceException(Exception):
    """ Exception for failed inference """

    def __init__(self, err: str, obj: object) -> None:
        name = obj.__class__.__name__
        file = i.getfile(obj.__class__)
        where = f"(class: {name}) (file: '{file}')"
        super().__init__(err, where, "Consider setting the {generic} field in the class.")

class Generic(t.Generic[T]):
    _generic: t.Optional[t.Type[T]] = None

    @value
    def generic(self) -> t.Type[T]:
        if not self._generic:
            self._generic = _generic(self)
        return self._generic

    @value
    def genericName(self) -> str:
        try:
            return self.generic.__name__
        except InferenceException:
            return "Unknown"

def _generic(obj: t.Generic[T]) -> t.Type[T]:
    # Get Typed Class
    origin = getattr(obj, '__orig_class__', None)
    if origin is None:
        raise InferenceException("Cannot infer generic", obj)

    # Get Type Tuple
    generics = origin.__args__
    if len(generics) != 1:
        raise InferenceException("Too many generics", obj)

    # Return First Generic
    return generics[0]
