from typing import Dict, Optional, Type, TypeVar
from .error import ParseError
from .indent import Fmt
from .struct import Struct
from .literal import String
from .generic import Generic
from .parsable import Parsable
from .types import Any, isMap
from .utils import safeParse


class PolymorphicMeta(type):
    __DERIVED__: 'Dict[str, Type[PolymorphicStruct]]'


class PolymorphicStruct(Struct, metaclass=PolymorphicMeta):
    """ Direct Polymorphic type, requires Polymorphic as a container """
    type: String

    def __init_subclass__(cls, type: Optional[str] = None, abstract: bool = False) -> None:
        # Check if we are set up
        if not hasattr(cls, '__DERIVED__'):
            setattr(cls, '__DERIVED__', {})
            abstract |= type is None

        # Do not register abstract classes
        if abstract:
            return

        # Type needs to be specified
        assert type is not None, "Polymorphic subclasses must specify {TYPE: str} or {abstract: bool}"

        # Check that we dont override
        map = cls.__DERIVED__
        assert type not in map, "Redefing types is not supported!"

        # Register
        map[type] = cls


S = TypeVar('S', bound=PolymorphicStruct)


class Polymorphic(Parsable, Generic[S]):
    """ The container for PolymorphicStruct """
    _value: Optional[S] = None

    def require(self) -> S:
        if self._value is None:
            err = f"Polymorphic[{self.genericName}] is missing!"
            raise ParseError(err)
        return self._value

    def get(self) -> Optional[S]:
        return self._value

    def typeOf(self, data: Any):
        # Require Properties
        if not isMap(data):
            raise ParseError("Expected a Map")

        # Get the type mapping
        derived = self.generic.__DERIVED__

        # Get the actual type
        type = data.get('type')
        if type is None:
            raise ParseError("Type is not specified!")

        if type not in derived:
            derived = ", ".join(derived)
            raise ParseError(f"Type must be one of: {derived}")

        return derived[type]

    @safeParse
    def parse(self, data: Any):
        data = data or {}

        # Get old instance
        V = self._value
        self._value = None
        self.changed = False

        # Get target Type
        T = self.typeOf(data)

        # Reuse old or create new Instance
        if isinstance(V, T):
            self._value = V
        else:
            self._value = T()

        # Parse Data
        self.link(self._value, data)

    def format(self, F: Fmt) -> str:
        text = "None" if self._value is None else self._value.format(F)
        return self.what or text
