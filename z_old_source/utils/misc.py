import numpy as np
from .types import int3

rng = np.random.default_rng()


def random_box(volume: int3, l: int, h: int) -> tuple[int3, int3]:
    S: 'np.ndarray[np.int32]' = \
        np.array(volume, np.int32)  # type: ignore
    L = np.minimum(S, l)  # type: ignore
    H = np.minimum(S, h)  # type: ignore
    V = rng.integers(L, H + 1)  # type: ignore
    O = rng.integers(0, 1 + S - V)  # type: ignore
    return tuple(V), tuple(O) # type: ignore
