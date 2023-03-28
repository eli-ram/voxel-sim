from enum import Enum, auto

class Operation(Enum):
    CUTOUT = auto()
    INSIDE = auto()
    OUTSIDE = auto()
    OVERWRITE = auto()
