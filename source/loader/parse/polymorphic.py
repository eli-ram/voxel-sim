from typing import Any, Dict, Optional, Type, TypeVar
from .error import ParseError
from .indent import Fmt
from .struct import Struct
from .literal import String
from .generic import Generic
from .parsable import Parsable
from . import utils

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
        assert type is not None, "Polymorphic subclasses must specify {TYPE: str}, or {abstract: bool}"

        # Check that we dont override
        map = cls.__DERIVED__
        assert type not in map, "Redefing types is not supported!"

        # Register
        map[type] = cls

S = TypeVar('S', bound=PolymorphicStruct)

class Polymorphic(Parsable, Generic[S]):
    """ The container for PolymorphicStruct """
    type: Optional[S] = None

    @utils.safeParse
    def parse(self, data: Any):
        # Check for None
        if data is None:
            self.changed = self.type is not None
            self.type = None
            return
        
        self.changed = False

        # Require Properties
        if not utils.isMap(data):
            raise ParseError("Expected a Map")

        # Get the type mapping
        types = self.generic().__DERIVED__

        # Get the actual type
        type = data.get('type')
        if type is None:
            raise ParseError("Type is not specified!")

        if type not in types:
            types = ", ".join(types)
            raise ParseError(f"Type must be one of: {types}")

        cls = types[type]

        # Initialize the actual class & not this wrapper
        if not isinstance(self.type, cls):
            self.type = cls()

        # Parse Data
        utils.linkParse(self, self.type, data)

    def format(self, F: Fmt) -> str:
        text = "none" if self.type is None else self.type.format(F)
        return self.what + text