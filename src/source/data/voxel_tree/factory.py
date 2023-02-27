# [UNUSED CODE]


import abc

from .box import Box
from .data import Data


class Factory(abc.ABC):
    # NOTE: this class is not actually useful

    @abc.abstractmethod
    def get_box(self) -> Box: ...

    @abc.abstractmethod
    def fill_data(self, data: Data): ...

    def build(self):
        data = Data.Empty(self.get_box())
        self.fill_data(data)
        return data


class Mesh(Factory):
    """ Mesh-flow
    - Transform mesh to define box
    - Transform mesh to 3d-raster
    """

    def __init__(self) -> None:
        super().__init__()

class Function(Factory):
    """ Functional-flow
    - Transform function to define box
    - Inverse Transform coords to sample function
    """ 
