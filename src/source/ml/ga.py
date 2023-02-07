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

import source.ml.rng as r
import source.math.fields as f
import source.data.voxels as v
import source.data.material as m
import source.math.voxels2truss as v2t
import source.math.truss2stress as fem
import source.data.voxel_tree.node as n

from source.utils.types import bool3, float3


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

    # physics constraints
    forces: dict[m.Material, float3]
    statics: dict[m.Material, bool3]

    # setup
    seed: int | None
    size: int

    def seedPopulation(self, rng):
        print("[config] creating a population of size", self.size)
        # Points for A & B
        A = r.make_unit_points(rng, self.size)
        B = r.make_unit_points(rng, self.size)
        return A, B

    def iterPopulation(self, population):
        # Cylinders between A & B
        for (a, b) in zip(*population, strict=True):
            yield glm.vec3(a), glm.vec3(b)

    def createInduvidual(self, genome:  tuple[glm.vec3, glm.vec3]):

        # unpack points
        a, b = genome

        # Create Cylinder field
        field = f.Cylinder(
            self.mat_a * a,
            self.mat_b * b,
        )

        # field region
        B = self.node.data.box

        # field transform
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
        voxels.forces = self.forces
        voxels.statics = self.statics

        # done
        return voxels

    def evaluateInduvidual(self, individual: v.Voxels):
        # TODO: multiprocess this function
        # it's the easiest way to speedup the search

        # build truss
        truss = v2t.voxels2truss(individual)

        # sinmulate [todo: multiprocess this]
        # {deformation, edge-compression}
        D, E = fem.fem_simulate(truss)

        # unable to solve
        if E is None:
            return 1E10

        # fitness modifiers
        mods = 0.0

        # detect nan values
        N = np.isnan(E)

        # fix nan values if present
        # and punish bad solutions
        if N.any():
            E[N] = 0.0
            mods = 1E2

        # get min-max of compression
        max = E.max()
        min = E.min()

        # get mean of stress
        mean = abs(E).mean()

        # print(" max:", max)
        # print(" min:", min)
        # print(" mean:", mean)

        # fitness is based on
        # minimizing distortion
        # lower is better
        fitness = abs(max) + abs(min) + mean + mods

        # done
        return fitness

    def selectPopulation(self, rng, population, results):
        A, B = population

        # get sorted indices of results
        # low to high
        I = np.argsort(results)

        # fourths + rest
        size = self.size
        part = size // 4
        rest = size % 4
        # print(f"{size=} {part=} {rest=}")

        # top indices
        T = I[:part]
        best_a = A[T]
        best_b = B[T]
        # print('T', len(T))

        # rng indices
        R = I[rng.integers(part, self.size, part)]
        rand_a = A[R]
        rand_b = B[R]
        # print('R', len(R))

        # rest
        rest_a = r.make_unit_points(rng, rest)
        rest_b = r.make_unit_points(rng, rest)

        # build population (w/ crossover)
        A = np.concatenate([best_a, best_a, rand_a, rand_a, rest_a])
        B = np.concatenate([best_b, rand_b, best_b, rand_b, rest_b])
        # print('A', len(A))

        # new population
        return A, B

    def mutatePopulation(self, rng, population, generation):
        A, B = population

        # mutation amount (* unit-rng)
        amount = 0.1 / (1 + generation)

        # number of mutations
        count = self.size // 4

        # indices of mutations
        I = rng.integers(0, self.size, count)

        # mutate indices
        A[I] = r.move_unit_points(rng, A[I], amount)
        B[I] = r.move_unit_points(rng, B[I], amount)

        # result
        return A, B


class GA:

    def __init__(self, config: Config):
        self.reset(config)

    def reset(self, config: Config):
        self.rng = np.random.default_rng(config.seed)
        self.config = config
        self.population = config.seedPopulation(self.rng)
        self.generation = 0

    def step(self):
        C = self.config

        print(f"[generation-{self.generation}] running:")

        # Storage for fitness
        results = np.zeros(C.size, np.float32)

        # Iterate genomes
        genomes = C.iterPopulation(self.population)
        for i, genome in enumerate(genomes):
            # print(f"[genome-{i}] evaluating:")
            # Create induvidual
            individual = C.createInduvidual(genome)
            # Evaluate induvidual (fitness-function)
            evaluation = C.evaluateInduvidual(individual)
            # Store result
            print(f"[genome-{i}] result: {evaluation:3.3f}")
            results[i] = evaluation

        print(f"[generation-{self.generation}] results:")
        print("max:", results.max())
        print("mean:", results.mean())
        print("min:", results.min())
        # TODO: track trends

        # select population based on fitness
        self.population = C.selectPopulation(
            self.rng, self.population, results)

        # mutate population based on generation
        self.population = C.mutatePopulation(
            self.rng, self.population, self.generation)

        # update counter
        self.generation += 1
