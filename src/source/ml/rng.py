import numpy as np

from source.utils.types import Array, F

Points = Array[F]


class UnitSphere:

    def __init__(self, seed: int | None) -> None:
        self.rng = np.random.default_rng(seed)

    def make_points(self, size: int):
        # [N](x, y, z)
        P: Points = self.rng.uniform(-1.0, 1.0, size=(size, 3))

        # Check if points outside unit cirle
        I = np.sum(P * P, axis=1) > 1.0

        # Regenerate until all points are inside unit circle
        while C := I.sum():  # type: ignore
            P[I, :] = self.rng.uniform(-1, 1, size=(C, 3))
            I = np.sum(P * P, axis=1) > 1.0

        # ok
        return P

    def move_points(self, P: Points, max: float):
        # [N](x, y, z)
        S = P.shape
        assert len(S) == 2 and S[1] == 3, "array is not a list of points"

        # Move randomly
        P += self.make_points(len(P)) * max

        # Check if points outside unit cirle
        I = np.sum(P * P, axis=1) > 1.0

        # Clamp points outside of unit circle
        if I.any():
            P[I, :] *= 1 / np.linalg.norm(P[:, I], axis=1)  # type: ignore

        # ok
        return P
