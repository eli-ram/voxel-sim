import os
import numpy as np

from source.data.mesh import Geometry, Mesh
from pywavefront import (  # type: ignore
    wavefront as w,
    mesh as m,
    material as l,
)

__cache__ = dict[str, Mesh]()

def cacheMesh(file: str):
    """ Load or get Cached mesh """
    path = os.path.abspath(file)
    if path not in __cache__:
        __cache__[path] = loadMesh(file)
    return __cache__[path]

def loadMesh(file: str, cache: bool = False):
    """ Only load the first mesh """
    return next(yieldMeshes(file, cache))

def loadMeshes(file: str, cache: bool = False):
    """ Load all the meshes """
    return list(yieldMeshes(file, cache))

def yieldMeshes(file: str, cache: bool = False):
    """ Discard all other data then mesh data """
    # Allow the creation of cache files, must be deleted manually
    scene = w.Wavefront(file, cache=cache)


    meshes: list[m.Mesh] = scene.mesh_list
    
    for mesh in meshes:
        yield getSimpleMesh(mesh)


def getSimpleMesh(mesh: m.Mesh):
    """ Convert mesh to simple mesh """
    materials: list[l.Material] = getattr(mesh, 'materials')
    vertices = [getVertices(material) for material in materials]
    stacked = np.vstack(vertices)

    # Split stacked vertices into vertex array & index array
    V, I = np.unique(stacked, return_inverse=True, axis=0)
    U = I.astype(np.uint32)
    
    return Mesh(V, U, Geometry.Triangles)


def getVertices(m: l.Material) -> 'np.ndarray[np.float32]':
    """ Extract vertices from material """
    # Get Vertices ordered in rows
    vertices = np.array(m.vertices, dtype=np.float32)  # type: ignore
    vertices = np.reshape(vertices, (-1, m.vertex_size))

    # Cut out everything except position
    return vertices[:, -3:]
