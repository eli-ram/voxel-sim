import typing as t
import inspect as i

T = t.TypeVar('T')


class InferenceException(Exception):
    """ Exception for failed inference """

    def __init__(self, err: str, obj: object) -> None:
        name = obj.__class__.__name__
        file = i.getfile(obj.__class__)
        where = f"(class: {name}) (file: '{file}')"
        option = "Consider setting the {generic} field in the class."
        super().__init__(err, where, option)  


class Generic(t.Generic[T]):

    def __init__(self) -> None:
        if not hasattr(self.__class__, 'generic'):
            self.generic = Generic.load(self)

    @staticmethod
    def load(obj: 'Generic[T]') -> t.Type[T]:
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

    @staticmethod
    def get(obj: 'Generic[T]') -> t.Type[T]:
        if not hasattr(obj, 'generic'):
            setattr(obj, 'generic', Generic.load(obj))
        return getattr(obj, 'generic')

    @staticmethod
    def name(obj: 'Generic[T]') -> str:
        try:
            return Generic.get(obj).__name__
        except InferenceException:
            return "Unknown"
