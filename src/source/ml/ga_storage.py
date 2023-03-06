from typing import Generic, TypeVar, Protocol, Any
from dataclasses import dataclass
import numpy as np
import glm
import os
import re

A = list[float]
T = TypeVar('T')


class Storage(Generic[T], Protocol):
    """ Data storage serialization protocol """
    def deserialize(self, data: A) -> T: ...
    def serialize(self, value: T) -> A: ...


@dataclass
class Induvidual(Generic[T]):
    """ A individual with a genome and a fitness """
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
        assert value.validated, \
            """ Trying to serialize a unvalidated induvidual """
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
    """ A generation of induviduals """
    population: list[Induvidual[T]]
    index: int

    def size(self):
        return len(self.population)

    def sort(self):
        self.population.sort(key=lambda i: i.fitness)



class GenerationStorage(Generic[T], Storage[Generation[T]]):
    def __init__(self, genome: Storage[T]) -> None:
        self.individual = InduvidualStorage(genome)

    def serialize(self, value: Generation[T]) -> list[list[float]]:
        return [self.individual.serialize(I) for I in value.population]

    def deserialize(self, data: list[list[float]], index: int) -> Generation[T]:
        return Generation([self.individual.deserialize(I) for I in data], index)


class Database(Generic[T]):
    """ A folder based storage for genetic algorithm generations """
    FILENAME = "generation.{}.npy"
    REGEX = re.compile(r"^generation\.(\d+)\.npy$")

    def __init__(self, storage: Storage[T], folder: str):
        # Add subfolder
        folder = os.path.join(folder, "ga")
        
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
        """ Format the generation as a filepath """
        filename = self.FILENAME.format(generation)
        return os.path.join(self.__folder, filename)

    def generations(self):
        """ Return the number of generations """
        return self.__generations

    def load(self, generation: int):
        """ Load a specific generation from file """
        # Get file for generation
        file = self.__file(generation)
        assert os.path.isfile(file), \
            f"Could not load generation, file does not exist! ('{file}')"

        # Load data using numpy utils
        data: Any = np.load(file)
        
        # Force 2D array
        if len(data.shape) == 1:
            data = [data]

        # Deserialize
        return self.__storage.deserialize(data, generation)

    def loadAll(self):
        """ Load all generations from file """
        return [self.load(i) for i in range(self.__generations)]

    def loadLast(self):
        """ Load last generation from file """
        if self.__generations == 0:
            raise IndexError("There is no generations")
        return self.load(self.__generations - 1)

    def save(self, generation: Generation[T]):
        """ Save a generation to file as the new Last generation """
        assert generation.index == self.__generations, \
            f""" Generation has unexpected index (expected: {self.__generations} found: {generation.index})"""
        data = self.__storage.serialize(generation)
        file = self.__file(self.__generations)
        np.save(file, np.array(data), allow_pickle=False)
        self.__generations += 1

    def empty(self):
        """ Check if no generations are saved """
        return self.__generations == 0        

    def fitness(self, generations: 'list[Generation[T]]'):
        """ Get the fitness array for a list of generations """
        return np.array([[I.fitness for I in G.population] for G in generations])

    def parameters(self, generations: 'list[Generation[T]]'):
        """ Get the parameter array for a list of generations """
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

    G = Generation([new() for _ in range(8)], db.generations())
    db.save(G)
    print(db.generations())

    generations = db.loadAll()
    for i, g in enumerate(generations):
        A = g.population[0].fitness
        g.sort()
        B = g.population[0].fitness
        print(i, A, '->', B)

    F = db.fitness(generations)

    def fmt(t, V):
        print(t, " ".join(f"{v:6.3f}" for v in V))

    fmt("mean", F.mean(axis=1))
    fmt("less", F.min(axis=1))
    fmt("parm", db.parameters(generations).std(axis=1).mean(axis=1))
