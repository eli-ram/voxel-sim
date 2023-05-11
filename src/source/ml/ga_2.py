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


@dataclass
class Genome:
    a: glm.vec3
    b: glm.vec3

    @classmethod
    def random(cls, rng, size: int):
        A, B = np.split(r.make_unit_points(rng, size * 2), 2)
        return [cls(glm.vec3(a), glm.vec3(b)) for a, b in zip(A, B)]


class GenomeStorage(s.Storage[Genome]):

    def serialize(self, genome: Genome) -> s.Data:
        return [*genome.a, *genome.b]

    def deserialize(self, data: s.Data) -> Genome:
        a1, a2, a3, b1, b2, b3 = data
        return Genome(glm.vec3(a1, a2, a3), glm.vec3(b1, b2, b3))


Storage = GenomeStorage()


def open_db(folder: str):
    """ Open the Database w/ this GenomeStorage """
    return s.Database(Storage, folder)


@dataclass
class Config:
    """ Genetic Algorithm Configuration """
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
    keep: int
    mutations: int

    # output
    folder: str

    def __post_init__(self):
        # Make sure keep is inside valid range
        self.keep = max(self.keep, 0)
        self.keep = min(self.keep, self.size // 4)

        # Make sure mutations is inside valid range
        self.mutations = max(self.mutations, 0)

    def seedPopulation(self, rng):
        print("[config] creating a population of size", self.size)
        P = s.Induvidual.package(Genome.random(rng, self.size))
        return s.Generation(P, 0)

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

    def evaluate(self, phenome: v.Voxels):
        # TODO: multiprocess this function
        # it's the easiest way to speedup the search

        # build truss
        truss = v2t.voxels2truss(phenome)

        try:
            # sinmulate [todo: multiprocess this]
            # {deformation, edge-compression}
            D, E = fem.fem_simulate(truss)
        except Exception as e:
            print(e)
            return 1E10

        # No Solution        
        if E is None:
            return 1E10

        # Invalid Solution
        if not np.isfinite(E).all(): # type: ignore
            return 1E10

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
        fitness = abs(max) + abs(min) + mean

        # done
        return fitness

    def selectPopulation(self, rng, generation: s.Generation[Genome]):

        # fourths + rest
        size = generation.size()
        keep = self.keep
        rest = size - (keep * 4)
        # print(f"{size=} {part=} {rest=}")

        # top indices (assumes sorted population)
        best = generation.population[:keep]

        # rng indices
        R = rng.integers(keep, size, keep)
        rand = [generation.population[i] for i in R]

        # rest
        rest = s.Induvidual.package(Genome.random(rng, rest))

        # crossover
        def crossover(A: list[s.Induvidual[Genome]], B: list[s.Induvidual[Genome]]):
            return s.Induvidual.package(
                Genome(a.genome.a, b.genome.b) 
                for a, b in zip(A, B, strict=True)
            )

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
        amount = 1 / (1 + generation.index)

        # size
        size = generation.size()

        # number of mutations
        count = self.mutations

        # cutoff position (ignore new individuals)
        cutoff = self.keep * 4

        # list of genomes to mutate (spare the best genome)
        idxs: list[int] = rng.integers(1, cutoff, count)
        picks = [generation.population[i] for i in idxs]

        # list of moves for mutation
        moves = Genome.random(rng, count)

        # mutate gene
        def mutate(g: glm.vec3, m: glm.vec3):
            v = g + (m * amount)
            l = glm.length(v)
            return v / l if l > 1.0 else v

        # indices of mutations
        for I, M in zip(picks, moves):
            G = I.genome
            # Mutate
            G.a = mutate(G.a, M.a)
            G.b = mutate(G.b, M.b)
            # Invalidate
            I.validated = False

        # result
        return generation

    def getFolder(self):
        """ Allow using datetime to format the folder name """
        # Example: "test{now:[%Y-%m-%d][%H-%M]}"
        return self.folder.format(now=datetime.now())


class GA:

    def __init__(self, config: Config):
        self.running = False
        self.reset(config)

    def reset(self, C: Config):
        self.db = open_db(C.getFolder())
        self.rng = np.random.default_rng(C.seed)
        self.best = None
        self.config = C

        # Initialize / Load Generation
        if self.db.empty():
            print("Creating first Generation")
            G = C.seedPopulation(self.rng)
        else:
            print("Loading last Generation")
            G = self.db.loadLast().sorted()
            G = C.selectPopulation(self.rng, G)
            G = C.mutatePopulation(self.rng, G)

        assert G.size() == C.size, \
            f"Stored population has different size: {G.size()}"            

        self.generation = G
        # Environment may have changed...
        # force full re-evaluation
        self.generation.invalidate()

    def current(self):
        if best := self.best:
            return self.config.presentInduvidual(best.genome)

    def step(self):
        R, self.running = self.running, True

        # This is used as a task
        # Duplicated execution is not allowed
        if R:
            return

        C = self.config
        G = self.generation

        print(f"\n[generation-{G.index}] running:")

        # Iterate genomes
        for i, I in enumerate(G.population):
            if not I.validated:
                # Realize induvidual
                phenotype = C.createPhenotype(I.genome)
                # Evaluate induvidual (fitness-function)
                I.fitness = C.evaluate(phenotype)

            op = 'cached' if I.validated else 'result'
            print(f"[genome-{i}] {op}: {I.fitness:6.3f}")
            I.validated = True

        # order population
        G = G.sorted()

        # Save progression data
        self.db.save(G)

        # Update best result (always at 0 when sorted)
        best = G.population[0]
        if self.best is None or self.best.fitness > best.fitness:
            self.best = best

        # select population based on fitness
        G = C.selectPopulation(self.rng, G)

        # mutate population based on generation
        G = C.mutatePopulation(self.rng, G)

        # store generation
        self.generation = G

        # stop running
        self.running = False

        # present best induvidual
        return C.presentInduvidual(self.best.genome)


if __name__ == '__main__':
    # Simple test code to
    # check the SimpleGenome
    from os import path

    folder = path.dirname(__file__)
    folder = path.join(folder, '..', '..', '..', 'results')
    print(folder)
    if not path.isdir(folder):
        raise NotADirectoryError(folder)

    # Initialize folder db, in 'test' subfolder
    db = s.Database(Storage, path.join(folder, 'test'))
    print(db.generations())

    rng = np.random.default_rng()

    def __generation(rng, size: int, index: int):
        G = Genome.random(rng, size)
        F = rng.random(size) * 100
        P = [s.Induvidual(g, f, True) for g, f in zip(G, F)]
        return s.Generation(P, index)

    db.save(__generation(rng, 8, db.generations()).sorted())
    print(db.generations())

    generations = db.loadAll()
    for i, g in enumerate(generations):
        print(i, g.population[0])

    F = db.fitness(generations)

    def fmt(t, V):
        print(t+':', " ".join(f"{v:6.3f}" for v in V))

    fmt("mean", F.mean(axis=1))
    fmt("less", F.min(axis=1))
    fmt("parm", db.parameters(generations).std(axis=1).mean(axis=1))
