"""
Genetic Algorithm

1. population
2. fitness
3. selection
4. reproduction
5. mutation


"""

import glm
import numpy as np
from dataclasses import dataclass

import source.ml.rng as rng
import source.math.fields as f
import source.data.voxels as v
import source.data.material as m
import source.loader.material as l_m
import source.math.voxels2truss as v2t
import source.math.truss2stress as fem
import source.data.voxel_tree.node as n

# directly using loader store


@dataclass
class Config:
    # rod transform
    matrix: glm.mat4

    # rod width
    width: float

    # rod endpoints
    mat_a: glm.mat4
    mat_b: glm.mat4

    # rod material
    material: m.Material

    # rod operation
    op: n.Operation

    # input voxels
    node: n.VoxelNode

    # all materials
    materials: l_m.MaterialStore

    # setup
    seed: int | None
    size: int

    def seedRng(self):
        return rng.UnitSphere(self.seed)

    def seedPopulation(self, rng: rng.UnitSphere):
        # Points for A & B
        return rng.make_points(self.size * 2)

    def iterPopulation(self, population):
        S = self.size
        # Cylinders between A & B
        for (a, b) in zip(population[:S], population[S:]):
            yield glm.vec3(a), glm.vec3(b)

    def createInduvidual(self, genome:  tuple[glm.vec3, glm.vec3]):
        # get constant internals
        M = self.materials
        B = self.node.data.box

        # unpack points
        a, b = genome

        # Create Cylinder field
        field = f.Cylinder(
            self.mat_a * glm.vec3(a),
            self.mat_b * glm.vec3(b),
        )

        # Correct field params
        matrix = glm.translate(-glm.vec3(B.start)) * self.matrix

        # Compute field
        grid = field.compute(B.shape, matrix, self.width)

        # Bundle as data w/ correct offset
        data = n.Data \
            .FromMaterialGrid(self.material, grid) \
            .offset(B.start)

        # Bundle as node
        node = n.VoxelNode(self.op, data)

        # Join with computed node
        data = n.VoxelNode.process([self.node, node])

        # build voxels
        voxels = v.Voxels(data.material.shape)

        # Set internals
        voxels.grid = data.material
        voxels.strength = data.strength
        voxels.forces = M.forces
        voxels.statics = M.statics

        # done
        return voxels

    def evaluateInduvidual(self, individual: v.Voxels):

        # build truss
        truss = v2t.voxels2truss(individual)

        # sinmulate [todo: multiprocess this]
        D, E = fem.fem_simulate(truss)


class GA:

    def __init__(self, config: Config):
        self.rng = config.seedRng()
        self.config = config
        self.population = config.seedPopulation(self.rng)

    def step(self):
        C = self.config

        for genome in C.iterPopulation(self.population):
            individual = C.createInduvidual(genome)
            evaluation = C.evaluateInduvidual(individual)
            print(evaluation)



        pass


if __name__ == '__main__':
    M = glm.mat4()
    C = Config(
        matrix=M,
        width=1.0,
        mat_a=M,
        mat_b=M,
        material=m.Material(1, "<bad>", m.Color(0, 0, 0), 1.0),
        op=n.Operation.OVERWRITE,
        node=n.VoxelNode.Empty(),
        materials=l_m.MaterialStore(),
        seed=None,
        size=32,
    )
    R = C.seedRng()
    P = C.seedPopulation(R)
    print(P.shape)
    for i, genome in enumerate(C.iterPopulation(P)):
        print(i, genome)

    a = n.Operation.OUTSIDE
    b = n.Operation.INSIDE
    print(a == b)

    from dataclasses import asdict
    new = Config(**asdict(C))
    new.width = 0.1

    print(C == C)
    print(C == new)
