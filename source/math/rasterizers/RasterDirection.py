from ...utils.types import int3
from enum import Enum

class Raster_Direction_3D(Enum):
    X = (1, 2, 0), (2, 0, 1)
    Y = (2, 0, 1), (1, 2, 0)
    Z = (0, 1, 2), (0, 1, 2)

    @property
    def swizzle(self) -> slice:
        return self.value[0]

    @property
    def transpose(self) -> int3:
        return self.value[1]

    def reshape(self, shape: int3) -> int3:
        S = [shape[i] for i in self.value[0]]
        return tuple(S)  # type: ignore