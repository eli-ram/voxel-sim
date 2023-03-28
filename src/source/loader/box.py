
import source.parser.all as p
import source.data.voxel_tree.box as b


class Int3(p.Value[b.int3]):

    def fromNone(self):
        return None

    def fromMap(self, data):
        def g(k):
            return int(data.get(k, 0))
        return g('x'), g('y'), g('z')

    def fromArray(self, data):
        def g(i):
            return int(data[i])
        return g(0), g(1), g(2)

    def fromValue(self, data):
        v = int(data)
        return v, v, v

    def toString(self, value: b.int3):
        x, y, z = value
        return f"({x}, {y}, {z})"


class Int2(p.Value[b.int2]):
    def fromNone(self):
        return None

    def fromMap(self, data):
        def g(k):
            return int(data.get(k, 0))
        return g('x'), g('y')

    def fromArray(self, data):
        def g(i):
            return int(data[i])
        return g(0), g(1)

    def fromValue(self, data):
        v = int(data)
        return v, v

    def toString(self, value: b.int2):
        x, y = value
        return f"({x}, {y})"


class Box(p.Struct):
    box = b.Box.Empty()

    # Option 1:
    start: Int3
    stop: Int3

    # Option 2:
    offset: Int3
    shape: Int3

    # Option 3:
    x: Int2
    y: Int2
    z: Int2

    # Else:
    # => Empty

    def get(self):
        return self.box

    def _make(self):
        # Lying a bit about the types here
        # as x,y,z are Int2 not int3
        # also using the struct internal _fields ...
        d: dict[str, Int3] = self._fields  # type: ignore

        s = {k: v for k, g in d.items() if (v := g.get())}

        if {} == s.keys():
            return b.Box.Empty()

        if {'offset', 'shape'} == s.keys():
            return b.Box.OffsetShape(**s)

        if {'start', 'stop'} == s.keys():
            return b.Box.StartStop(**s)

        if {'x', 'y', 'z'} == s.keys():
            ranges = zip(s['x'], s['y'], s['z'])
            start, stop = [(x, y, z) for x, y, z in ranges]
            return b.Box.StartStop(start, stop)

        err = "Invalid combination! Use (start, stop) or (offset, shape) or (x, y, z)"
        raise p.ParseError(err)

    def postParse(self):
        self.box = self._make()
