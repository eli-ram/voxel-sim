"""
Genetic Algorithm

1. population
2. fitness
3. selection
4. reproduction
5. mutation


"""

import os
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
from source.loader.geometry import Context
from source.utils.types import bool3, float3

import source.ml.ga_storage as s

Genome = s.SimpleGenome
Storage = s.SimpleStorage()


def new(a, b):
    return s.Induvidual.new(Genome(glm.vec3(a), glm.vec3(b)))


def random_genomes(rng, size: int):
    A, B = np.split(r.make_unit_points(rng, size * 2), 2)
    return [Genome(glm.vec3(a), glm.vec3(b)) for a, b in zip(A, B)]


def random_induviduals(rng, size: int):
    return [s.Induvidual.new(G) for G in random_genomes(rng, size)]


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
    folder: str

    def seedPopulation(self, rng):
        print("[config] creating a population of size", self.size)
        return s.Generation(random_induviduals(rng, self.size), 0)

    def presentInduvidual(self, genome: Genome):
        # Create Cylinder field
        field = f.Cylinder(
            self.mat_a * genome.a,
            self.mat_b * genome.b,
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

    def createPhenotype(self, genome: Genome):
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

    def evaluate(self, individual: v.Voxels):
        # TODO: multiprocess this function
        # it's the easiest way to speedup the search

        # build truss
        truss = v2t.voxels2truss(individual)

        try:
            # sinmulate [todo: multiprocess this]
            # {deformation, edge-compression}
            D, E = fem.fem_simulate(truss)
        except Exception as e:
            print(e)
            return 1E10

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

    def bestInduvidual(self, generation: s.Generation[Genome]):
        # sort low to high
        generation.sort()

        # Lowest is best
        return generation.population[0]

    def selectPopulation(self, rng, generation: s.Generation[Genome]):
        # sort low to high
        generation.sort()

        # fourths + rest
        size = generation.size()
        part = (size // 5)
        rest = (size % 5) + part
        # print(f"{size=} {part=} {rest=}")

        # top indices
        best = generation.population[:part]

        # rng indices
        # R = I[rng.integers(part, self.size, part)]
        R = rng.integers(part, self.size, part)
        rand = [generation.population[i] for i in R]
        # print('R', len(R))

        # rest
        rest = random_induviduals(rng, rest)

        # crossover
        def crossover(A: list[s.Induvidual[Genome]], B: list[s.Induvidual[Genome]]):
            return [new(a.genome.a, b.genome.b) for a, b in zip(A, B, strict=True)]

        # build population w/ crossover
        return s.Generation([
            *best,
            *rand,
            *crossover(best, rand),
            *crossover(rand, best),
            *rest,
        ], generation.index + 1)

    def mutatePopulation(self, rng, generation: s.Generation[Genome]):
        # mutation amount (* unit-rng)
        amount = 10 / (1 + generation.index)

        # size
        size = generation.size()

        # number of mutations
        count = size // 4

        # cutoff position (ignore new individuals)
        cutoff = (size // 5) + (size % 5)

        # list of genomes to mutate
        I = rng.integers(0, cutoff, count)
        induviduals = [generation.population[i] for i in I]

        # list of moves for mutation
        moves = random_genomes(rng, count)

        # mutate gene
        def mutate(g: glm.vec3, m: glm.vec3):
            v = g + (m * amount)
            l = glm.length(v)
            return v / l if l > 1.0 else v

        # indices of mutations
        for I, M in zip(induviduals, moves):
            G = I.genome
            # Mutate
            G.a = mutate(G.a, M.a)
            G.b = mutate(G.b, M.b)
            # Invalidate
            I.validated = False

        # result
        return generation

    def getFolder(self):
        now = datetime.now()
        return f'{self.folder}{now:[%Y-%m-%d][%H-%M]}'


class GA:

    def __init__(self, config: Config):
        self.running = False
        self.reset(config)

    def reset(self, config: Config):
        self.rng = np.random.default_rng(config.seed)
        self.config = config
        self.generation = config.seedPopulation(self.rng)
        self.best = None
        self.db = s.Database(Storage, config.getFolder())

    def current(self):
        if best := self.best:
            return self.config.presentInduvidual(best.genome)

    def step(self):
        R, self.running = self.running, True

        # don't run twice ...
        if R:
            return

        C = self.config

        print(f"\n[generation-{self.generation.index}] running:")

        # Iterate genomes
        for i, I in enumerate(self.generation.population):
            if not I.validated:
                # Realize induvidual
                phenotype = C.createPhenotype(I.genome)
                # Evaluate induvidual (fitness-function)
                I.fitness = C.evaluate(phenotype)

            op = 'cached' if I.validated else 'result'
            print(f"[genome-{i}] {op}: {I.fitness:6.3f}")
            I.validated = True

        # Save progression data
        # self.generation.sort()
        self.db.save(self.generation)

        # Update best result
        best = C.bestInduvidual(self.generation)
        if self.best is None or self.best.fitness > best.fitness:
            self.best = best

        # select population based on fitness
        self.generation = C.selectPopulation(self.rng, self.generation)

        # mutate population based on generation
        self.generation = C.mutatePopulation(self.rng, self.generation)

        # stop running
        self.running = False

        # present best induvidual
        return C.presentInduvidual(self.best.genome)
