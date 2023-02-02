
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
            return s.Void()
    return wrap


class Context:

    def __init__(self, box: b.Box):
        # store box
        self.box = box
        # store shape
        self.shape = box.shape
        # start with offset
        self.matrix = glm.translate(
            -glm.vec3(*box.start)
        )

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
        O = self.box.start
        B = node.data.box
        # Offset box
        B.start += O
        B.stop += O
        # Return node
        return node


class Geometry(p.PolymorphicStruct):
    # Voxel operation (not supported)
    # operation: p.String

    # Voxel Material Key
    material: MaterialKey

    # Geometry Transform
    transform: Transform

    # Show origin
    show_origin: p.Bool

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
    def getRender(self) -> s.Render:
        # Render a Wireframe
        mesh = self.getMesh()
        color = self.material.get().color
        matrix = self.transform.matrix

        # build model
        model = Wireframe(mesh).setColor(color)

        # include debug origins
        if (debugs := self.transform.debugs):
            scene = s.Scene(matrix, children=[model])
            O = Origin()
            for (matrix, _) in debugs:
                M = glm.affineInverse(matrix)
                scene.add(s.Transform(M, O))
            return scene

        # return model
        return s.Transform(matrix, model)

    def getVoxels(self, ctx: Context) -> n.VoxelNode:
        impl = self.__class__.__name__
        raise NotImplementedError(f"{impl}.getVoxels()")
