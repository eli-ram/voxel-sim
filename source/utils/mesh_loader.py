import numpy as np
from .mesh.simplemesh import Geometry, SimpleMesh
from pywavefront import (  # type: ignore
    wavefront as w,
    mesh as m,
    material as l,
)


def loadMeshes(file: str, cache: bool = False):
    """ Discard all other data then mesh data """
    # Allow the creation of cache files, must be deleted manually
    scene = w.Wavefront(file, cache=cache)

    meshes: list[m.Mesh] = getattr(scene, 'mesh_list')

    for mesh in meshes:
        yield getSimpleMesh(mesh)


def getSimpleMesh(mesh: m.Mesh):
    """ Convert mesh to simple mesh """
    materials: list[l.Material] = getattr(mesh, 'materials')
    vertices = [getVertices(material) for material in materials]
    stacked = np.vstack(vertices)

    # Split stacked vertices into vertex array & index array
    V, I = np.unique(stacked, return_inverse=True, axis=0)
    U: np.ndarray[np.uint16] = I.astype(np.uint16) # type: ignore

    return SimpleMesh(V, U, Geometry.Triangles)


def getVertices(material: l.Material) -> 'np.ndarray[np.float32]':
    """ Extract vertices from material """
    values = getattr(material, 'vertices')
    vertex_size = getattr(material, 'vertex_size')
    # Get Vertices ordered in rows
    vertices = np.array(values, dtype=np.float32)  # type: ignore
    vertices = np.reshape(vertices, (-1, vertex_size))

    # Cut out everything except position
    return vertices[:, -3:]
