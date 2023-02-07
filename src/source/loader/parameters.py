from typing import Callable, TypeVar, Generic
import glm
import numpy as np

import source.parser.all as p
import source.math.utils as u
import source.utils.types as t
import source.utils.shapes as shp
import source.loader.material as m
import source.loader.geometry as g
import source.interactive.scene as s
import source.data.voxel_tree.node as n
import source.math.fields as f
import source.ml.ga as ga

from source.ml.rng import UnitSphere
from source.utils.wireframe.wireframe import Wireframe
from source.loader.transforms.sequence import Transform
from source.loader.data import Color

T = TypeVar('T')


class Cache(Generic[T]):
    def opt(self) -> T | None:
        return getattr(self, '__value', None)

    def set(self) -> bool:
        return hasattr(self, '__value')

    def __call__(self) -> T:
        return getattr(self, '__value')

    def cache(self, value: T):
        setattr(self, '__value', value)
        return value


class Lazy(Generic[T]):

    def __init__(self, fn: Callable[[], T]):
        self.__fn = fn

    def get(self) -> T:
        if not hasattr(self, '__value'):
            setattr(self, '__value', self.__fn())
        return getattr(self, '__value')


class Volume(p.Struct):
    color: Color
    width: p.Float
    transform: Transform

    _model = Lazy(lambda: Wireframe(shp.sphere_2(64)))

    def render(self):
        M = self._model.get() \
            .setColor(self.color.require()) \
            .setWidth(self.width.getOr(1.0))
        return self.transform.package(M)


class Parameters(p.Struct):
    """ Genetic algorithm parameters """
    # Rng seed
    seed: p.Int
    # Show info
    show: p.Bool
    # Global transform
    transform: Transform
    # Volume transforms
    volume_a: Volume
    volume_b: Volume
    # Material
    material: m.MaterialKey
    operation: g.Operation
    width: p.Float

    # internals
    _rng = UnitSphere(None)

    def postParse(self) -> None:
        self._rng = UnitSphere(self.seed.get())

    def loadMaterial(self, store: m.m.MaterialStore):
        self.setError(self.material.load(store))
        print(self.material.get())

    def render(self):
        if not self.show.get():
            return None

        T = self.transform
        return s.Scene(T.matrix, [
            self.volume_a.render(),
            self.volume_b.render(),
            *T.getDebugs()
        ])

    def sample(self, ctx: g.Context):
        ctx = ctx.push(self.transform.matrix)
        # random points
        A, B = self._rng.make_points(2)
        # define field
        F = f.Cylinder(
            self.volume_a.transform.matrix * glm.vec3(*A),
            self.volume_b.transform.matrix * glm.vec3(*B),
        )
        # get width
        width = self.width.getOr(1.0)
        # compute voxels
        G = F.compute(ctx.shape, ctx.matrix, width)
        # get material
        M = self.material.get()
        # get operation
        O = self.operation.require()
        # box data
        D = n.Data.FromMaterialGrid(M, G)
        # Operation
        return n.VoxelNode.Leaf(O, D)

    def generateGenome(self, count: int):
        config = ga.Config(
            self.volume_a.transform.matrix,
            self.volume_b.transform.matrix,
        )

        print(config)


if __name__ == "__main__":
    # U = UnitSphere(None)
    # P = U.make_points(1000)
    # X = U.make_points(2)
    pass




