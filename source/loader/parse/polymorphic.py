from .struct import Struct
from .literal import String, Float, Int
from .error import ParseError
from .utils import safeParse, generic, linkParse
from .indent import Fmt
from .parsable import Parsable
from typing import Any, Dict, Generic, Optional, Type, TypeVar, cast

class PolymorphicMeta(type):
    __DERIVED__: 'Dict[str, Type[PolymorphicStruct]]'

class PolymorphicStruct(Struct, metaclass=PolymorphicMeta):
    """ Direct Polymorphic type, requires Polymorphic as a container """
    type: String

    def __init_subclass__(cls, TYPE: Optional[str] = None, abstract: bool = False) -> None:
        # Check if we are set up
        if not hasattr(cls, '__DERIVED__'):
            setattr(cls, '__DERIVED__', {})
            abstract |= TYPE is None

        # Do not register abstract classes
        if abstract:
            return 

        # Type needs to be specified
        assert TYPE is not None, "Polymorphic subclasses must specify {TYPE: str}, or {abstract: bool}"

        # Check that we dont override
        map = cls.__DERIVED__
        assert TYPE not in map, "Redefing types is not supported!"

        # Register
        map[TYPE] = cls

S = TypeVar('S', bound=PolymorphicStruct)

class Polymorphic(Parsable, Generic[S]):
    """ The container for PolymorphicStruct """
    type: Optional[S] = None

    @safeParse
    def parse(self, data: Any):
        # Check for None
        if data is None:
            self.changed = self.type is not None
            self.type = None
            return

        # Require Properties
        if not isinstance(data, dict):
            raise ParseError("Expected a Map")

        props = cast(Dict[str, Any], data)
        T = cast(PolymorphicMeta, generic(self))
        types = T.__DERIVED__

        # Get the actual type
        type = props.get('type')
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
        linkParse(self, self.type, props)

    def format(self, F: Fmt) -> str:
        text = "" if self.type is None else self.type.format(F)
        return self.what + text

class Base(PolymorphicStruct):
    name: String

class Test_1(Base, TYPE="test-1"):
    value: Float

class Test_2(Base, TYPE="test-2"):
    value: Int

class Test_3(Test_1, TYPE="test-3"):
    extra: String

class Test(Struct):
    p: Polymorphic[Base]

def test_init():
    print(*Base.__DERIVED__)

    test = Test()
    test.parse(dict(p={
        "type": "test-1",
        "name": "hello",
        "value": 2.1,
    }))
    print(test)
    test.parse(dict(p={
        "type": "test-3",
        "name": "hello",
        "value": 2.5,
        "extra": "world",
    }))
    print(test)
