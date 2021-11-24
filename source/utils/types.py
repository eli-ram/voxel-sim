from typing import Tuple, Union
import numpy as _np

# Grouped Ints
int1 = Tuple[int]
int2 = Tuple[int, int]
int3 = Tuple[int, int, int]
intN = Tuple[int, ...]

# Grouped Bools
bool3 = Tuple[bool, bool, bool]


# Numpy support types
Array = _np.ndarray
F = Union[_np.float16, _np.float32, _np.float64]
I = Union[_np.int8, _np.int16, _np.int32, _np.int64]
U = Union[_np.uint8, _np.uint16, _np.uint32, _np.uint64]


