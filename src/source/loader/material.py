from typing import NamedTuple

import source.parser.all as p
import source.utils.types as t
import source.data.material as m
from .data import Color, Vec3


class Locks(NamedTuple):
    x: bool = False
    y: bool = False
    z: bool = False


class Material(p.Struct):
    color: Color
    strength: p.Float
    locks: p.Value[Locks]
    force: Vec3


class MaterialKey(p.String):
    _cache: m.Material

    def load(self, store: m.MaterialStore):
        """Load the material from the store"""
        with self.captureErrors():
            key = self.maybe()

            if key is None:
                raise p.ParseError("Missing material key!")

            if key not in store:
                raise p.ParseError(f"Material does not exist! (key: {key})")

            self._cache = store[key]

    def get(self):
        """Get the cached material"""
        return self._cache


class MaterialStore(p.Map[Material]):
    generic = Material

    # Caches
    store: m.MaterialStore
    forces: dict[m.Material, t.float3]
    statics: dict[m.Material, t.bool3]

    def postParse(self):
        # New caches
        store = m.MaterialStore()
        forces = dict[m.Material, t.float3]()
        statics = dict[m.Material, t.bool3]()

        # PINK = m.Color(255 / 255, 192 / 255, 203 / 255, 1000)

        # Listed materials
        for key, V in self:
            color = V.color.require().copy()

            # MATERIAL SPACING
            store.create(f"__{key}__1", color, 0.0)

            # Register material
            M = store.create(
                key,
                color,
                V.strength.getOr(0.0),
                # V.force.get(),
                # V.locks.get(),
            )

            # MATERIAL SPACING
            store.create(f"__{key}__2", color, 0.0)

            # Bind forces
            if F := V.force.get():
                forces[M] = (F.x, F.y, F.z)

            # Bind locks
            if L := V.locks.get():
                statics[M] = (L.x, L.y, L.z)

        # Save caches
        self.store = store
        self.forces = forces
        self.statics = statics

    def get(self):
        return self.store

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, MaterialStore):
            return False

        # NOTE
        # {store} does not contribute here ...
        # as we're interested in other changes

        return self.forces == o.forces and self.statics == o.statics
