from typing import Any, Dict, List, TypeVar
from .indent import Indent
from .parsable import Parsable

P = TypeVar('P', bound=Parsable)

class Fmt:

    @staticmethod
    def fmt(V: Dict[str, str], I: Indent) -> str:
        W = len(V) and max(len(k) for k in V) + 1
        return "".join(I + k.ljust(W) + v for k, v in V.items())

    @classmethod
    def LiteralDict(cls, V: Dict[str, Any], I: Indent) -> str:
        return cls.fmt({f"{k}:": str(v) for k, v in V.items()}, I)

    @classmethod
    def LiteralList(cls, V: List[Any], I: Indent) -> str:
        return cls.fmt({f"[{i}]:": str(v) for i, v in enumerate(V)}, I)

    @classmethod
    def ParsableDict(cls, V: Dict[str, P], I: Indent) -> str:
        N = I.next()
        return cls.fmt({f"{k}:": v.format(N) for k, v in V.items()}, I)

    @classmethod
    def ParsableList(cls, V: List[P], I: Indent) -> str:
        N = I.next()
        return cls.fmt({f"[{i}]:": v.format(N) for i, v in enumerate(V)}, I)
