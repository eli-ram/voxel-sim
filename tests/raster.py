import __init__
from source.math.scanline import IntRasterizer
from timeit import default_timer as tick

from gl_voxels import bone as get_bone
from source.utils.wireframe import SimpleMesh
bone: SimpleMesh = get_bone()

I = bone.indices.reshape(-1, 3)
vertices = bone.vertices * 100 + 30
vertices = vertices.astype(int).reshape(-1, 3)
vertices = vertices[:, ::2]

start = tick()
size = (90, 90)
raster = IntRasterizer(size)
for tri in I:
    a, b, c, d, e, f = vertices[tri, :].flatten()
    raster.rasterize((a, b), (c, d), (e, f))
stop = tick()

total = stop - start
print(raster.text())
print("Count: ", len(I))
print("Timing: ", total, total / len(I))

# TRY:
# https://youtu.be/eviSykqSUUw?t=2257