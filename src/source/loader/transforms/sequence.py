from .variants import p, glm, Options

class Transform(p.Array[Options]):
    """A sequence of transformations"""
    generic = Options
    matrix = glm.mat4()
    debugs: list[tuple[glm.mat4, str]] = []

    def postParse(self) -> None:
        m = glm.mat4()
        d = []

        # Combine the sequence to one matrix
        for item in self:
            I = item.require()
            if I.debug:
                d.append((glm.mat4(m), I.name()))
            elif I.postmul:
                m = m * I.matrix
            else:
                m = I.matrix * m

        # Update internals
        self.matrix = m
        self.debugs = d

        # Debug print
        for (matrix, name) in d:
            print(f"\n<debug:transform> '{name}'\n{matrix}")
