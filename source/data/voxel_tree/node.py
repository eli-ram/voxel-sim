from __future__ import annotations

from typing import List

import numpy as np

from .box import Box
from .impl import impl
from .operation import Operation


class VoxelNode:
    op: Operation
    box: Box
    mask: np.ndarray[np.bool_]

    @classmethod
    def Leaf(cls, op: Operation, box: Box, mask: np.ndarray[np.bool_]):
        new = box.crop(mask)
        return cls(op, new, mask[box.slice(new)])

    @classmethod
    def Parent(cls, op: Operation, nodes: List[VoxelNode]):
        box = Box.combine([node.box for node in nodes])
        mask = np.full(box.shape, False)
        parent = cls(op, box, mask)
        for child in nodes:
            child.apply_to(parent)
        return parent


    def __init__(self, op: Operation, box: Box, mask: np.ndarray[np.bool_]):
        self.op = op
        self.box = box
        self.mask = mask

    def apply_to(self, node: VoxelNode):
        PB = node.box
        SB = self.box
        OP = impl.get(self.op)
        P = node.mask[PB.slice(SB)]
        S = self.mask[SB.slice(PB)]
        mask = OP.where(P, S)
        P[mask] = S[mask]

def test_nodes():
    def v(a, b, c):
        return np.array([a, b, c], np.int64)
    
    RNG = np.random.default_rng()
    C = np.arange(2).astype(np.bool_)

    def rng(a, b):
        box = Box(a, b)
        mask = RNG.choice(C, size=box.shape) # type: ignore
        return VoxelNode.Leaf(Operation.OVERWRITE, box, mask)

    def log(node: VoxelNode):
        print(node.op)
        print(node.box, node.box.shape)
        print(node.mask.astype(int))

    A = rng(v(0, 0, 0), v(2, 2, 2))
    log(A)

    B = rng(v(0, 0, 0), v(2, 2, 2))
    log(B)

    C = VoxelNode.Parent(Operation.INSIDE, [A, B])
    log(C)
