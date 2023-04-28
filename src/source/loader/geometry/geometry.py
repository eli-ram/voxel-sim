
from traceback import print_exc
import source.data.voxel_tree.box as b
from source.utils.wireframe.origin import Origin

import source.data.voxel_tree.node as n
from source.utils.wireframe.wireframe import Wireframe
from source.interactive import (
    scene as s,
)
from source.data import (
    material as m,
    mesh,
)

from source.parser import all as p
from ..material import MaterialKey
from ..transforms.sequence import Transform, glm


def void_on_error(method):
    def wrap(self: 'Geometry', *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except:
            print_exc()
            return s.Void
    return wrap


class Context:

    def __init__(self, box: b.Box):
        # store box (TODO: __box)
        self.box = box

        # store shape
        self.shape = box.shape

        # start with offset
        self.matrix = glm.translate(
            -glm.vec3(*box.start)
        )

        # Everything from (0, 0, 0) until shape
        # is considered inside bounds
        # it's not needed to voxelize
        # anything outside the bounds

    def push(self, mat: glm.mat4):
        new = Context(self.box)
        new.matrix = self.matrix * mat
        return new

    def eq(self, other: 'Context'):
        return (
            self.shape == other.shape and
            self.matrix == other.matrix
        )

    def finalize(self, node: n.VoxelNode):
        return node.offset(self.box.start)
    
    def __eq__(self, o: object) -> bool:
        return isinstance(o, Context) and self.eq(o)


class Operation(p.Value[n.Operation]):
    _ = n.Operation

    table = {
        'add': _.OVERWRITE,
        'overwrite': _.OVERWRITE,
        'inside': _.INSIDE,
        'outside': _.OUTSIDE,
        'cut': _.CUTOUT,
        'cutout': _.CUTOUT,
        # todo:
        # invert / inverse ?
        #
    }

    def parseValue(self, data):

        # Overwrite by default
        if data is None:
            return self._.OVERWRITE

        # require string
        if not isinstance(data, str):
            raise p.ParseError("must be a string")

        # preprocess
        K = data.strip().lower()
        T = self.table

        # check
        if K not in T:
            keys = ",".join(f'"{k}"' for k in T.keys())
            raise p.ParseError(f"unknown key (valid: {keys})")

        return T[K]


class Geometry(p.PolymorphicStruct):
    # Voxel Material Key
    material: MaterialKey

    # Geometry Transform
    transform: Transform

    # Voxel operation
    operation: Operation

    # Toggles
    render: p.Bool
    voxels: p.Bool

    # Cache buster for Context
    __cache = Context(n.Box.Empty())

    def _cacheCtx(self, ctx: Context):
        """ Push transform onto Context & Return previous Context """
        # Load prev context
        old = self.__cache
        # Create new context
        new = ctx.push(self.transform.matrix)
        # Cache new context
        self.__cache = new
        # Return (new, old)
        return new, old

    def loadMaterial(self, store: m.MaterialStore):
        self.setError(self.material.load(store))

    def getMesh(self) -> mesh.Mesh:
        raise NotImplementedError()

    @void_on_error
    def buildRender(self) -> s.Render:
        if not self.render.getOr(True):
            return s.Void

        # Render a Wireframe
        mesh = self.getMesh()
        color = self.material.get().color
        matrix = self.transform.matrix

        # build model (TODO cache buffers --> change wireframe api ....)
        model = Wireframe(mesh).setColor(color)

        # include debug origins, if found
        if debugs := self.transform.getDebugs():
            return s.Scene(matrix, children=[*debugs, model])

        # return model
        return s.Transform(matrix, model)

    def buildVoxels(self, ctx: Context) -> n.VoxelNode:
        if not self.voxels.getOr(True):
            return n.VoxelNode.Empty()
        impl = self.__class__.__name__
        raise NotImplementedError(f"{impl}.getVoxels()")
