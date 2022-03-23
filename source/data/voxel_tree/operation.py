from enum import Enum, auto

class Operation(Enum):
    INSIDE = auto()
    OUTSIDE = auto()
    OVERWRITE = auto()
