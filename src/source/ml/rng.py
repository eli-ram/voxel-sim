import numpy as np

from source.utils.types import Array, F

Points = Array[F]
RNG = np.random.Generator

def seed_rng(seed: int | None):
    return np.random.default_rng(seed)


def make_unit_points(rng: RNG, size: int) -> Points:
    # [N](x, y, z)
    P = rng.uniform(-1.0, 1.0, size=(size, 3))

    # Check if points outside unit cirle
    I = np.sum(P * P, axis=1) > 1.0

    # Regenerate until all points are inside unit circle
    while C := I.sum():  # type: ignore
        P[I] = rng.uniform(-1, 1, size=(C, 3))
        I = np.sum(P * P, axis=1) > 1.0

    # ok
    return P


def move_unit_points(rng: RNG, P: Points, max: float) -> Points:
    # [N](x, y, z)
    S = P.shape
    assert len(S) == 2 and S[1] == 3, "array is not a list of points"

    # Move randomly
    P += make_unit_points(rng, len(P)) * max

    # Check if points outside unit cirle
    I = np.sum(P * P, axis=1) > 1.0

    # Clamp points outside of unit circle
    if I.any():
        P[I] *= 1 / np.linalg.norm(P[I], axis=1)  # type: ignore

    # ok
    return P
