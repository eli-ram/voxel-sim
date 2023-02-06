import source.interactive.scene as s
import source.data.voxel_tree.node as n
import source.parser.all as p
from source.utils.wireframe.origin import Origin

from .geometry import Geometry, Context


class GeometryCollection(Geometry, type='collection'):
    """ Compose Geometry from child instances """

    # There is no material for a composition
    material: None

    # The list of children
    elements: p.Array[p.Polymorphic[Geometry]]

    # Voxel cache
    __node: n.VoxelNode

    def __iter__(self):
        for element in self.elements:
            G = element.get()
            if G is None or G.hasError():
                continue
            yield G

    def loadMaterial(self, store):
        for element in self:
            element.loadMaterial(store)

    def buildRender(self) -> s.Render:
        if not self.render.getOr(True):
            return s.Void

        # Build children
        L = [G.buildRender() for G in self if G.render.getOr(True)]
        # include debug origins
        L += self.transform.getDebugs()
        # Build the scene
        return s.Scene(self.transform.matrix, L)

    def buildVoxels(self, ctx: Context) -> n.VoxelNode:
        if not self.voxels.getOr(True):
            return n.VoxelNode.Empty()

        # Push transform
        ctx, old = self._cacheCtx(ctx)

        changed = (
            not ctx.eq(old)
            or any(G.hasChanged() for G in self)
            or self.operation.hasChanged()
        )

        # Compute if changed
        if changed:
            # Get Children
            L = [G.buildVoxels(ctx) for G in self if G.voxels.getOr(True)]
            # Get Operation
            O = self.operation.require()
            # Build Voxels
            N = n.VoxelNode.Parent(O, L)
            # cache node
            self.__node = N

        # return cached node
        return self.__node
