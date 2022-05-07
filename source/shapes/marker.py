from source.data.mesh import Mesh, Geometry, v, i

def LowHighCenter(L: float, H: float, C: float):
    return Mesh(
        vertices=v(
            [C, C, H],
            [C, C, L],
            [C, H, C],
            [C, L, C],
            [H, C, C],
            [L, C, C],
        ),
        indices=i(
            [0, 1],
            [2, 3],
            [4, 5],
        ),
        geometry=Geometry.Lines,
    )


def Origin(size: float):
    return LowHighCenter(-size, size, 0)

def ReferenceFrame():
    return LowHighCenter(0, 1, 0)