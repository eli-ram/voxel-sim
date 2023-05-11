from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Tuple, Union

import numpy as np

from .box import Box
from ..material import Material

int3 = Tuple[int, int, int]


@dataclass(eq=False)
class Data:
    # The position & volume of the data
    box: Box
    # Where this data exists
    mask: np.ndarray[np.bool_]
    # What material this data is made from
    material: np.ndarray[np.uint32]
    # The strength of the data
    strength: np.ndarray[np.float64]

    def arrays(self) -> Tuple[np.ndarray, ...]:
        """Iterate over the data arrays"""
        return (self.mask, self.material, self.strength)

    def __post_init__(self):
        """Verify the data"""
        shape = self.box.shape

        # Require all arrays to have the same shape as the box
        if not all(a.shape == shape for a in self.arrays()):
            # Debug data
            name = self.__class__.__name__
            print(f"{name}:")
            for k, v in asdict(self).items():
                print(f" - {k}:", v.shape)
            # Raise error
            err = " All data members does not have the same shape. "
            raise AttributeError(err)

    @classmethod
    def Empty(cls, box: Box) -> Data:
        """Create a data object where all values are set to zero"""
        shape = box.shape
        return cls(
            box=box,
            mask=np.zeros(shape, np.bool_),
            material=np.zeros(shape, np.uint32),
            strength=np.zeros(shape, np.float64),
        )

    @classmethod
    def FromMaterialGrid(cls, mat: Material, grid: np.ndarray[np.bool_]):
        full = Box.OffsetShape((0, 0, 0), grid.shape)
        box = full.crop(grid)
        grid = grid[full.slice(box)]
        return cls(
            box=box,
            mask=grid,
            material=(grid * mat.id).astype(np.uint32),
            strength=(grid * mat.strenght).astype(np.float64),
        )

    def crop(self) -> Data:
        """Crop this data based on it's mask"""
        return self[self.box.crop(self.mask)]

    def offset(self, amount: "np.ndarray[np.int64]"):
        return Data(
            box=self.box.offset(amount),
            mask=self.mask,
            material=self.material,
            strength=self.strength,
        )

    def __getitem__(self, box: Box) -> Data:
        """Get the slice that overlaps the other data"""
        slices = self.box.slice(box)
        return Data(
            box=box,
            mask=self.mask[slices],
            material=self.material[slices],
            strength=self.strength[slices],
        )

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Data):
            return False

        A = self.arrays()
        B = self.arrays()
        if len(A) != len(B):
            print("Data.__eq__ different types !")
            return False

        return self.box == o.box and all(np.array_equal(a, b) for a, b in zip(A, B))
