from dataclasses import dataclass

from ..vector import Vec3, Vec4
from ..parse import all as p
import glm

# What if Blender Plugin


class Mat:

    matrix = glm.mat4()


class Scale(Mat, Vec3):

    def postParse(self) -> None:
        self.matrix = glm.scale(self.require())


class Translate(Mat, Vec3):

    def postParse(self) -> None:
        self.matrix = glm.translate(self.require())


class AxisAngleDegrees(Mat, Vec4):
    """ A Rotation based of Axis Angle w/ degrees 

    ```
    # Example value
    value = [0, 1, 0, 90]
    # Resulting Parameters
    axis = [0, 1, 0]
    angle = radians(90)
    ```

    """

    def postParse(self) -> None:
        value = self.require()
        self.matrix = glm.rotate(
            glm.radians(value.w), glm.vec3(value)
        )


class AxisAngleRadians(Mat, Vec4):
    """ A Rotation based of Axis Angle w/ radians 

    ```
    # Example value
    value = [0, 1, 0, pi]
    # Resulting Parameters
    axis = [0, 1, 0]
    angle = pi
    ```

    """

    def postParse(self) -> None:
        value = self.require()
        self.matrix = glm.rotate(
            value.w, glm.vec3(value)
        )


class RotateDegrees(Mat, p.Enum[p.Value[float]]):
    """ Rotate around X, Y or Z axis in Degrees """
    X: p.Value[float]
    Y: p.Value[float]
    Z: p.Value[float]

    def postParse(self) -> None:
        value = self.require().require()
        def _(dir): return float(dir == self.__active)
        self.matrix = glm.rotate(glm.radians(
            value), glm.vec3(_("X"), _("Y"), _("Z"))
        )


class RotateRadians(Mat, p.Enum[p.Value[float]]):
    """ Rotate around X, Y or Z axis in Radians """
    X: p.Value[float]
    Y: p.Value[float]
    Z: p.Value[float]

    def postParse(self) -> None:
        value = self.require().require()
        def _(dir): return float(dir == self.variant())
        self.matrix = glm.rotate(
            value, glm.vec3(_("X"), _("Y"), _("Z"))
        )


class Options(p.Enum[Mat]):
    # Scale
    scale: Scale
    # Translate
    translate: Translate
    # Rotate
    axisAngleDeg: AxisAngleDegrees
    axisAngleRad: AxisAngleRadians
    rotateDeg: RotateDegrees
    rotateRad: RotateRadians


class Sequence(p.Array[Options]):
    """A sequence of transformations"""
    matrix = glm.mat4()

    def postParse(self) -> None:
        # Combine the sequence to one matrix
        m = glm.mat4()
        for item in self:
            m *= item.require().matrix
        self.matrix = m
