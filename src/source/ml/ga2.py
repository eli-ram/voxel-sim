from typing import Generic, TypeVar, Protocol, cast
from dataclasses import dataclass
import numpy as np
import glm
import os
import re

A = list[float]
T = TypeVar('T')


class Storage(Generic[T], Protocol):
    def deserialize(self, data: A) -> T: ...
    def serialize(self, value: T) -> A: ...


@dataclass
class Induvidual(Generic[T]):
    genome: T
    fitness: float
    validated: bool

    @classmethod
    def new(cls, genome: T):
        return cls(genome, 0, False)


class InduvidualStorage(Generic[T], Storage[Induvidual[T]]):
    def __init__(self, genome: Storage[T]) -> None:
        self.genome = genome

    def serialize(self, value: Induvidual[T]) -> A:
        G = self.genome.serialize(value.genome)
        F = value.fitness
        return [F, *G]

    def deserialize(self, data: A) -> Induvidual[T]:
        F, *G = data
        return Induvidual(
            genome=self.genome.deserialize(G),
            fitness=F,
            validated=True,
        )


@dataclass
class Generation(Generic[T]):
    population: list[Induvidual[T]]

    def sort(self):
        self.population.sort(key=lambda i: i.fitness)


class GenerationStorage(Generic[T], Storage[Generation[T]]):
    def __init__(self, genome: Storage[T]) -> None:
        self.individual = InduvidualStorage(genome)

    def serialize(self, value: Generation[T]) -> list[list[float]]:
        return [self.individual.serialize(I) for I in value.population]

    def deserialize(self, data: list[list[float]]) -> Generation[T]:
        return Generation([self.individual.deserialize(I) for I in data])


class Database(Generic[T]):
    FILENAME = "generation.{}.values"
    REGEX = re.compile(r"^generation\.(\d+)\.values$")

    def __init__(self, storage: Storage[T], folder: str):
        # Setup internals
        self.__generations = 0
        self.__storage = GenerationStorage(storage)
        self.__folder = os.path.abspath(folder)

        # Recover saved data
        F = self.__folder
        os.makedirs(F, exist_ok=True)
        for E in os.listdir(F):
            M = self.REGEX.match(E)
            if M is None:
                continue
            G = int(M.group(1)) + 1
            if G > self.__generations:
                self.__generations = G

        # [end] __init__

    def __file(self, generation: int):
        filename = self.FILENAME.format(generation)
        return os.path.join(self.__folder, filename)

    def generations(self):
        return self.__generations

    def load(self, generation: int):
        # Get file for generation
        file = self.__file(generation)
        assert os.path.isfile(file), \
            f"Could not load generation, file does not exist! ('{file}')"

        # Load data using numpy utils
        data = np.loadtxt(file, dtype=np.float64)

        # Force 2D array
        if len(data.shape) == 1:
            data = [data]

        # Typecast ...
        data = cast(list[list[float]], data)

        # Deserialize
        return self.__storage.deserialize(data)

    def loadAll(self):
        return [self.load(i) for i in range(self.__generations)]

    def loadLast(self):
        if self.__generations == 0:
            raise IndexError("No generations are saved")
        return self.load(self.__generations - 1)

    def save(self, generation: Generation[T]):
        data = self.__storage.serialize(generation)
        file = self.__file(self.__generations)
        with open(file, "x") as f:
            f.writelines(" ".join(f"{v:.5f}" for v in R) + '\n' for R in data)
        self.__generations += 1

    def hasGenerations(self):
        return self.__generations > 0

    def fitness(self, generations: 'list[Generation[T]]'):
        return np.array([[I.fitness for I in G.population] for G in generations])

    def parameters(self, generations: 'list[Generation[T]]'):
        S = self.__storage.individual.genome
        return np.array([[S.serialize(I.genome) for I in G.population] for G in generations])


@dataclass
class SimpleGenome:
    a: glm.vec3
    b: glm.vec3


class SimpleStorage(Storage[SimpleGenome]):

    def serialize(self, genome: SimpleGenome) -> A:
        return [*genome.a, *genome.b]

    def deserialize(self, data: A) -> SimpleGenome:
        a1, a2, a3 = data[:3]
        b1, b2, b3 = data[3:]
        return SimpleGenome(
            a=glm.vec3(a1, a2, a3),
            b=glm.vec3(b1, b2, b3),
        )


if __name__ == '__main__':
    from random import random

    folder = os.path.dirname(__file__)
    folder = os.path.join(folder, 'results', 'test')
    print(folder)
    db = Database(SimpleStorage(), folder)
    print(db.generations())

    def r():
        return random() * 2.0 - 1.0

    def v():
        return glm.vec3(r(), r(), r())

    def new():
        return Induvidual(
            genome=SimpleGenome(v(), v()),
            fitness=random() * 100,
            validated=True,
        )

    G = Generation([new() for _ in range(8)])
    db.save(G)
    print(db.generations())

    generations = db.loadAll()
    for i, g in enumerate(generations):
        g.sort()
        print(i, g.population[0])

    F = db.fitness(generations)

    def fmt(t, V):
        print(t, " ".join(f"{v:6.3f}" for v in V))

    fmt("mean", F.mean(axis=1))
    fmt("less", F.min(axis=1))
    fmt("parm", db.parameters(generations).std(axis=1).mean(axis=1))
