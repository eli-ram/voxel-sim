from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Union

import numpy as np

from .box import Box

int3 = Tuple[int, int, int]


@dataclass
class Data:
    # The position & volume of the data
    box: Box
    # Where this data exists
    mask: np.ndarray[np.bool_]
    # What material this data is made from
    material: np.ndarray[np.uint32]
    # The strength of the data
    strength: np.ndarray[np.float32]

    def arrays(self) -> Tuple[np.ndarray, ...]:
        """ Iterate over the data arrays """
        return (self.mask, self.material, self.strength)

    def __post_init__(self):
        """ Verify the data """
        shape = self.box.shape
        assert all(a.shape == shape for a in self.arrays()), \
            " All data members does not have the same shape. "

    @classmethod
    def Empty(cls, box: Box) -> Data:
        """ Create a data object where all values are set to zero """
        shape = box.shape
        return cls(
            box=box,
            mask=np.zeros(shape, np.bool_),
            material=np.zeros(shape, np.uint32),
            strength=np.zeros(shape, np.float32),
        )

    def crop(self) -> Data:
        """ Crop this data based on it's mask """
        return self[self.box.crop(self.mask)]

    def __getitem__(self, box: Box) -> Data:
        """ Get the slice that overlaps the other data """
        slices = self.box.slice(box)
        return Data(
            box=box,
            mask=self.mask[slices],
            material=self.material[slices],
            strength=self.strength[slices],
        )
