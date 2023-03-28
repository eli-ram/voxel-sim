from __future__ import annotations
from dataclasses import dataclass

import numpy as np

from .box import Box
from .data import Data
from .impl import impl
from .operation import Operation


@dataclass
class VoxelNode:
    op: Operation
    data: Data

    @staticmethod
    def process(nodes: list[VoxelNode]) -> Data:
        """ Join a sequence of Voxel nodes to raw data """
        B = Box.Union([node.data.box for node in nodes])
        D = Data.Empty(B)
        for N in nodes:
            impl.get(N.op).apply(D, N.data)
        return D.crop()
    
    @classmethod
    def Empty(cls):
        """ Create a Voxel node with no volume """
        return cls(Operation.OVERWRITE, Data.Empty(Box.Empty()))

    @classmethod
    def Leaf(cls, op: Operation, data: Data):
        """ Create a Voxel node by raw data """
        return cls(op, data.crop())

    @classmethod
    def Parent(cls, op: Operation, nodes: list[VoxelNode]):
        """ Create a Voxel node by joining child nodes """
        return cls(op, cls.process(nodes))

    def offset(self, amount: 'np.ndarray[np.int64]'):
        """ Offset the voxel node by a vector [x, y, z] """
        return VoxelNode(self.op, self.data.offset(amount))

def test_nodes():
    """ (bad) Test method """
    from random import randrange

    def v(a, b, c):
        return np.array([a, b, c], np.int64)

    C = np.arange(2).astype(np.bool_)

    def rng(a, b):
        box = Box(a, b)
        data = Data.Empty(box)
        x, y, z = (randrange(0, l) for l in box.shape)
        data.mask[x, y, z] = True
        return VoxelNode.Leaf(Operation.OVERWRITE, data)

    def log(node: VoxelNode):
        print(node.op)
        print(node.data.box, node.data.box.shape)
        print(node.data.mask.astype(int))

    A = rng(v(0, 0, 0), v(2, 2, 2))
    log(A)

    B = rng(v(0, 2, 0), v(2, 4, 2))
    log(B)

    C = VoxelNode.Parent(Operation.INSIDE, [A, B])
    log(C)
