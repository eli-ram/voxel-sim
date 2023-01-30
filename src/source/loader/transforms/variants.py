from ..vector import Vec3, Vec4
from ..parse import all as p
import glm

# What if Blender Plugin


class Mat:
    matrix = glm.mat4()
    debug = False
    postmul = True
    def name(self) -> str: ...


class Scale(Mat, Vec3):

    def postParse(self) -> None:
        self.matrix = glm.scale(self.require())


class Translate(Mat, Vec3):

    def postParse(self) -> None:
        self.matrix = glm.translate(self.require())


class Degrees(p.Float):

    def radians(self):
        return glm.radians(self.require())


class Radians(p.Float):

    def radians(self):
        return self.require()


class Angle(p.Enum[Radians]):
    # short form
    deg: Degrees
    rad: Radians
    # long form
    degrees: Degrees
    radians: Radians

    def get(self):
        # Return radian interpretation
        return self.require().radians()


def _axis(_, *args, **kwgs):
    # Intercept string
    if len(args) == 1 and isinstance(args[0], str):
        K = args[0]
        def _(D): return float(D == K)
        return glm.vec3(_("X"), _("Y"), _("Z"))
    # Forward
    return glm.vec3(*args, **kwgs)


class Axis(Vec3):
    generic = _axis


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
