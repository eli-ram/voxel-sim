
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
        return f"({x=}, {y=}, {z=})"


class Box(p.Struct):
    box = b.Box.Empty()

    # Option 1:
    start: Int3
    stop: Int3

    # Option 2:
    offset: Int3
    shape: Int3

    # Else:
    # => Empty

    def get(self):
        return self.box

    def _make(self):
        offset = self.offset.get()
        shape = self.shape.get()
        start = self.start.get()
        stop = self.stop.get()
        err = "Don't specify both (start & stop) and (offset & shape)"

        if start and stop:
            if offset or shape:
                raise p.ParseError(err)
            return b.Box.StartStop(start, stop)

        if offset and shape:
            if start or stop:
                raise p.ParseError(err)
            return b.Box.OffsetShape(offset, shape)

        return b.Box.Empty()


    def postParse(self):
        self.box = self._make()
