import __init__
from source.math.linalg import unpack
from source.math.scanline import IntRasterizer
from timeit import default_timer as tick

from gl_voxels import bone as get_bone
from source.utils.wireframe.wireframe import SimpleMesh
bone: SimpleMesh = get_bone()

I = bone.indices.reshape(-1, 3)
vertices = bone.vertices * 45 + 37
vertices = vertices.astype(float).reshape(-1, 3)

start = tick()
size = (60, 60)
raster = IntRasterizer(size)
for tri in I:
    A, B, C = unpack(vertices[tri, :])
    raster.rasterize(A, B, C) # type: ignore
stop = tick()

total = stop - start
print(raster.text())
print("Count: ", len(I))
print("Timing: ", total, total / len(I))

# TRY:
# https://youtu.be/eviSykqSUUw?t=2257