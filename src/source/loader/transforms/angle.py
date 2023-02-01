import glm
import source.parser.all as p

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