from __future__ import annotations
from dataclasses import dataclass

from typing import List

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
    def process(nodes: List[VoxelNode]) -> Data:
        box = Box.Union(node.data.box for node in nodes)
        data = Data.Empty(box)
        for child in nodes:
            method = impl.get(child.op)
            method.apply(data, child.data)
        return data.crop()

    @classmethod
    def Leaf(cls, op: Operation, data: Data):
        return cls(op, data.crop())

    @classmethod
    def Parent(cls, op: Operation, nodes: List[VoxelNode]):
        return cls(op, cls.process(nodes).crop())


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
