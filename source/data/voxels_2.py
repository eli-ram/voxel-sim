from dataclasses import dataclass
from typing import Any, List, Tuple
import numpy as np

@dataclass
class VoxelNode:
    # Box Definition
    offset: np.ndarray[np.int64]
    shape: np.ndarray[np.int64]

    @property
    def min(self):
        return self.offset

    @property
    def max(self):
        return self.offset + self.shape

    def overlap(self, other: 'VoxelNode'):
        A = self.max > other.min
        B = self.min < other.max
        return (A & B).any()

    def data(self) -> Tuple[np.ndarray[Any], ...]:
        """ Voxel Data Iterator """
        return ()

    def __post_init__(self):
        # Require that the box is 3-dimensional
        assert self.shape.shape == (3,), \
            "Voxel shape must be 3 dimensional"
        assert self.offset.shape == (3,), \
            "Voxel offset must be 3 dimensional"

        # Require Data to fill the entire box
        shape = tuple(self.shape)
        for data in self.data():
            assert data.shape == shape, \
                "Voxel Data does not match box shape"

def boxOf(nodes: List[VoxelNode]):
    L = np.stack([n.min for n in nodes])
    low = L.min(axis=0)
    pass


@dataclass
class Voxels(VoxelNode):
    # Box Data
    grid: np.ndarray[np.float32]
    strength: np.ndarray[np.float32]

    def data(self):
        return self.grid, self.strength

    def apply(self, other: VoxelNode):

        if isinstance(other, Voxels):
            self.add(other)
        if isinstance(other, Void):
            self.remove(other)

    def add(self, other: 'Voxels'):
        pass

    def remove(self, other: 'Void'):
        pass


@dataclass
class Void(VoxelNode):
    # Box Data
    where: np.ndarray[np.bool_]

    def data(self):
        return self.where,
