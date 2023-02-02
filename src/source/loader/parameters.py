import numpy as np

import source.parser.all as p
import source.utils.types as t
from source.loader.geometry import Sphere


def _rng_unit_sphere(rng: np.random.Generator, size: int):
    # (x, y, z)[N]
    P: t.Array[t.F] = rng.uniform(-1.0, 1.0, size=(3, size))
    I = np.sum(P * P, axis=0) > 1.0

    # Regenerate until all points are inside unit circle
    while np.any(I):  # type: ignore
        P[:, I] = rng.uniform(-1, 1, size=(3, np.sum(I)))
        I = np.sum(P * P, axis=0) > 1.0

    # ok
    return P


def _cut_unit_sphere(P: t.Array[t.F]):
    I = np.sum(P * P, axis=0) > 1.0

    # Found points outside
    if np.any(I):  # type: ignore
        P[:, I] *= 1 / np.linalg.norm(P[:, I], axis=0) # type: ignore

    return P

def _rng_move(rng: np.random.Generator, range: float, size: int):
    return _rng_unit_sphere(rng, size) * range

class Parameters(p.Struct):
    """ Genetic algorithm parameters """
    seed: p.Int
    volume_1: Sphere
    volume_2: Sphere
    _rng = np.random.default_rng()

    def postParse(self) -> None:
        self._rng = np.random.default_rng(self.seed.get())

    def getRenders(self):
        return (
            self.volume_1.getRender(),
            self.volume_2.getRender(),
        )

    def generateGenome(self, count: int):
        P = _rng_unit_sphere(self._rng, count)
        print(np.linalg.norm(P, axis=0))
        PP = _cut_unit_sphere(P + P)
        print(np.linalg.norm(PP, axis=0))
        


if __name__ == "__main__":
    P = Parameters()

    P.generateGenome(5)
