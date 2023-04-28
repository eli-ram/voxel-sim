from .angle import Angle
from .axis import Axis, Vec3
from source.parser import all as p
import glm

# What if Blender Plugin


class Mat:
    """ Any matrix operation """
    matrix = glm.mat4()
    debug = False
    postmul = True
    def name(self) -> str: ...


class Scale(Mat, Vec3):
    """ Scale by a vector """

    def postParse(self) -> None:
        self.matrix = glm.scale(self.require())


class Translate(Mat, Vec3):
    """ Translate by a vector """

    def postParse(self) -> None:
        self.matrix = glm.translate(self.require())


class Rotate(Mat, p.Struct):
    """ Rotate around X, Y, Z or custom axis """
    axis: Axis
    angle: Angle
    local: p.Bool

    def postParse(self) -> None:
        axis = self.axis.require()
        angle = self.angle.get()
        self.matrix = glm.rotate(angle, axis)
        self.postmul = self.local.getOr(True)


class Debug(Mat, p.String):
    """Marker to debug transform stack"""
    debug = True

    def name(self) -> str:
        return self.getOr("unnamed")


class Options(p.Enum[Mat]):
    scale: Scale
    rotate: Rotate
    translate: Translate
    debug: Debug
