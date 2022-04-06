from source.data.voxel_tree import box
from .parse import all as p

class Int3(p.Value[box.int3]):

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

    def toString(self, value: box.int3):
        x, y, z = value
        return f"({x=}, {y=}, {z=})"


class Box(p.Struct):
    _value: box.Box

    # Option 1:
    start: Int3
    stop: Int3

    # Option 2:
    offset: Int3
    shape: Int3

    # Else:
    # => Empty

    def get(self):
        return self._value

    def _make(self):
        start = self.start.get()
        stop = self.stop.get()
        if start and stop:
            return box.Box.StartStop(start, stop)

        offset = self.offset.get()
        shape = self.shape.get()
        if offset and shape:
            return box.Box.OffsetShape(offset, shape)

        return box.Box.Empty()


    def postParse(self):
        self._value = self._make()
