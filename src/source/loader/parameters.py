import glm

import source.parser.all as p
import source.utils.shapes as shp
import source.loader.material as m
import source.loader.geometry as g
import source.interactive.scene as s
import source.data.voxel_tree.node as n
import source.math.fields as f
import source.loader.utils as u

import source.ml.rng as r
from source.utils.wireframe.wireframe import Wireframe
from source.loader.transforms.sequence import Transform
from source.loader.data import Color


class Volume(p.Struct):
    color: Color
    width: p.Float
    transform: Transform

    @u.cache
    def model(self):
        return Wireframe(shp.sphere_2(64))

    def render(self):
        M = self.model() \
            .setColor(self.color.require()) \
            .setWidth(self.width.getOr(1.0))
        return self.transform.package(M)


class Parameters(p.Struct):
    """ Genetic algorithm parameters """
    # Rng seed
    seed: p.Int
    population_size: p.Int

    # Show info
    show: p.Bool

    # Global transform
    transform: Transform

    # Point clouds
    # (used to sample )
    volume_a: Volume
    volume_b: Volume

    # Cylinder width
    width: p.Float

    # Material
    material: m.MaterialKey

    # Voxel operation
    operation: g.Operation

    def loadMaterial(self, store: m.m.MaterialStore):
        with self.captureErrors():
            self.material.load(store)
            print(self.material.get())

    def buildRender(self):
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
        rng = r.seed_rng(self.seed.get())
        # random points
        A, B = r.make_unit_points(rng, 2)
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
