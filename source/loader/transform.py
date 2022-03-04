from typing import Any
from .parse import AutoParsable, ValueParsable
import glm

class Position(ValueParsable[glm.vec3]):
    def parse(self, data: Any):
        self.value = glm.vec3()

class Rotation(ValueParsable[glm.quat]):
    def parse(self, data: Any):
        self.value = glm.quat()

class Scale(ValueParsable[glm.vec3]):
    def parse(self, data: Any):
        self.value = glm.vec3(1, 1, 1)

class Transform(AutoParsable):
    position: Position
    rotation: Rotation
    scale: Scale
