from typing import Tuple, TypeVar, Union
import numpy as _np

# Grouped Ints
int1 = Tuple[int]
int2 = Tuple[int, int]
int3 = Tuple[int, int, int]
intN = Tuple[int, ...]

# Grouped Floats
float1 = Tuple[float]
float2 = Tuple[float, float]
float3 = Tuple[float, float, float]
floatN = Tuple[float, ...]

# Grouped Bools
bool3 = Tuple[bool, bool, bool]


# Numpy support types
Array = _np.ndarray
F = Union[_np.float16, _np.float32, _np.float64]
I = Union[_np.int8, _np.int16, _np.int32, _np.int64]
U = Union[_np.uint8, _np.uint16, _np.uint32, _np.uint64]
N = Union[F, I, U]
T = TypeVar('T', bound='N')


