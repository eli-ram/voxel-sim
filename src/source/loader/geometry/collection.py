import source.interactive.scene as s
import source.data.voxel_tree.node as n
import source.parser.all as p

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

    def getRender(self) -> s.Scene:
        # Build children
        L = [G.getRender() for G in self]
        # Build the scene
        return s.Scene(self.transform.matrix, L)

    def getVoxels(self, ctx: Context) -> n.VoxelNode:
        # Push transform
        ctx, old = self._cacheCtx(ctx)
        # Check if cache is valid
        if ctx.eq(old) and not any(G.hasChanged() for G in self):
            return self.__node
        # Get Children
        L = [G.getVoxels(ctx) for G in self]
        # Get Operation
        O = n.Operation.OVERWRITE
        # Build Voxels (todo: cache)
        N = n.VoxelNode.Parent(O, L)
        self.__node = N
        return N
