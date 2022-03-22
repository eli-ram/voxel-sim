from .parse import all as p
from .parameters import Parameters
from .geometry import Geometry
from .material import Material


class Config(p.Struct):
    size: p.Int
    build: p.Bool
    render: p.Bool
    resolution: p.Int


class Configuration(p.Struct):
    # General Settings
    config: Config

    # Defined Materials
    materials: p.Map[Material]

    # Application order of Geometry
    geometry: p.Array[p.Polymorphic[Geometry]]

    # Machine Learning Parameters
    parameters: Parameters

    def postParse(self):
        for child in self.geometry:
            child.require().checkMaterials(self.materials.map)

    def log(self):
        print("Materials:")
        for key, value in self.materials:
            print(f"{key} => {value.color.value}")
        print("Geometry:")
        for index, value in enumerate(self.geometry.array):
            print(f"[{index}]:", end='')
            value.require().logMaterials(I="")
