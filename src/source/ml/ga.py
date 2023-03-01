"""
Genetic Algorithm

1. population
2. fitness
3. selection
4. reproduction
5. mutation


"""

from source.loader.geometry import Context
import glm
import numpy as np
from dataclasses import dataclass
from datetime import datetime

import source.ml.rng as r
import source.math.fields as f
import source.data.voxels as v
import source.data.material as m
import source.math.voxels2truss as v2t
import source.math.truss2stress as fem
import source.data.voxel_tree.node as n
from source.utils.directory import directory

from source.utils.types import bool3, float3

Genome = tuple[glm.vec3, glm.vec3]


# FIXME HOTFIX


@dataclass
class Config:
    # rod transform
    ctx: Context
    # matrix: glm.mat4

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

    # output
    filename: str

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

    def presentInduvidual(self, genome: Genome):
        # unpack points
        a, b = genome

        # Create Cylinder field
        field = f.Cylinder(
            self.mat_a * a,
            self.mat_b * b,
        )

        # field region
        # B = self.node.data.box
        ctx = self.ctx

        # field transform
        # matrix = glm.translate(-glm.vec3(*B.start)) * self.matrix

        # Compute field
        grid = field.compute(ctx.shape, ctx.matrix, self.width)

        # Bundle as data w/ correct offset
        data = n.Data.FromMaterialGrid(self.material, grid)

        # Bundle as node
        node = ctx.finalize(n.VoxelNode.Leaf(self.op, data))

        # Join with computed node
        return n.VoxelNode.process([self.node, node])

    def createInduvidual(self, genome: Genome):
        # creation & presentation uses same code
        data = self.presentInduvidual(genome)

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

    def bestInduvidual(self, population, results):
        A, B = population
        I = np.argmin(results)
        genome = (glm.vec3(A[I]), glm.vec3(B[I]))
        fitness = results[I]
        return genome, fitness

    def selectPopulation(self, rng, population, results):
        A, B = population

        # get sorted indices of results
        # low to high
        I = np.argsort(results)

        # fourths + rest
        size = self.size
        part = (size // 5)
        rest = (size % 5) + part
        # print(f"{size=} {part=} {rest=}")

        # top indices
        T = I[:part]
        best_a = A[T]
        best_b = B[T]
        # print('T', len(T))

        # rng indices
        # R = I[rng.integers(part, self.size, part)]
        R = I[rng.integers(part, self.size, part)]
        rand_a = A[R]
        rand_b = B[R]
        # print('R', len(R))

        # rest
        rest_a = r.make_unit_points(rng, rest)
        rest_b = r.make_unit_points(rng, rest)

        # build population (w/ crossover)
        A = np.concatenate([best_a,  rand_a, best_a, rand_a, rest_a])
        B = np.concatenate([best_b,  rand_b, rand_b, best_b, rest_b])
        # print('A', len(A))

        # new population
        return A, B

    def mutatePopulation(self, rng, population, generation):
        A, B = population

        # mutation amount (* unit-rng)
        amount = 10 / (1 + generation)

        # number of mutations
        count = self.size // 2

        # cutoff position (ignore new individuals)
        cutoff = (self.size // 5) + (self.size % 5)

        # indices of mutations
        I = rng.integers(0, cutoff, count)

        # mutate indices
        A[I] = r.move_unit_points(rng, A[I], amount)
        B[I] = r.move_unit_points(rng, B[I], amount)

        # result
        return A, B

    def createFilename(self, ext):
        now = datetime.now()
        return f'{self.filename}{now:[%Y-%m-%d][%H-%M]}{ext}'


_results_dir = ['']


def setResultsDir(dir: str):
    _results_dir[0] = dir


class GA:

    def __init__(self, config: Config):
        self.running = False
        self.reset(config)

    def reset(self, config: Config):
        self.rng = np.random.default_rng(config.seed)
        self.config = config
        self.population = config.seedPopulation(self.rng)
        self.generation = 0
        self.best_genome = None
        self.best_fitness = np.inf
        self.r_min = []
        self.r_mean = []
        self.r_max = []
        self.filename = config.createFilename('.txt')

        with directory(_results_dir[0]):
            with open(self.filename, "x") as f:
                pass

    def _append(self, results):
        with directory(_results_dir[0]):
            with open(self.filename, "a") as f:
                f.write(" ".join(f"{v:.5f}" for v in results) + "\n")

    def current(self):
        if genome := self.best_genome:
            return self.config.presentInduvidual(genome)

    def step(self):
        R, self.running = self.running, True

        # don't run twice ...
        if R:
            return

        C = self.config

        print(f"\n[generation-{self.generation}] running:")

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

        # Save progression data
        self._append(results)
        self.r_min.append(results.min())
        self.r_max.append(results.max())
        self.r_mean.append(results.mean())

        # Update best result
        genome, fitness = C.bestInduvidual(self.population, results)
        if self.best_genome is None or self.best_fitness > fitness:
            self.best_genome = genome
            self.best_fitness = fitness

        # Log data
        print(f"\n[generation-{self.generation}] results:")
        def _(l): return " -> ".join(f"{v:2.3f}" for v in l[-3:])
        print("  max:", _(self.r_max))
        print(" mean:", _(self.r_mean))
        print("  min:", _(self.r_min))
        # TODO: track trends

        # select population based on fitness
        self.population = C.selectPopulation(
            self.rng, self.population, results)

        # mutate population based on generation
        self.population = C.mutatePopulation(
            self.rng, self.population, self.generation)

        # update counter
        self.generation += 1

        # stop running
        self.running = False

        # present best induvidual
        return C.presentInduvidual(self.best_genome)
