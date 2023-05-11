from dataclasses import dataclass

from .colors import Color


@dataclass
class Material:
    id: int
    name: str
    color: Color
    strenght: float

    def __post_init__(self):
        assert self.id > 0, "Materials should never reference Voxel-VOID (0)"

    def __hash__(self):
        return self.id

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, Material):
            return False

        # NOTE
        # equality is determined
        # by physical properties
        # {strength}

        return self.id == o.id and self.strenght == o.strenght


class MaterialStore:
    def __init__(self):
        self._lut: dict[str, Material] = {}
        self._all: list[Material] = []

    def create(self, name: str, color: Color, strenght: float):
        assert name not in self._lut, " Material name is already occupied "
        L = len(self._all)
        M = Material(L + 1, name, color, strenght)
        self._lut[name] = M
        self._all.append(M)
        return M

    def updateOrCreate(self, name: str, color: Color, strength: float):
        if name in self._lut:
            M = self._lut[name]
            M.color = color
            return M
        return self.create(name, color, strength)

    def __contains__(self, key: str):
        return key in self._lut

    def __getitem__(self, key: str):
        return self._lut[key]

    def __iter__(self):
        yield from self._lut

    def colors(self):
        return Color.stack([m.color for m in self._all])
