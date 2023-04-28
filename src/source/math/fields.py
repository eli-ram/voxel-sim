# pyright: reportSelfClsParameterName=false
import typing as t
import numpy as np
import glm

from source.utils.types import Array, F, B, I, int3
import source.graphics.matrices as mat


class _(t.Any):
    """ Private namespace """

    # shorthand for any vector
    V = Array[F] | glm.vec3
    # Shorthand for newaxis
    ex = np.newaxis

    def coords(*shape: int):
        # Ranges
        R = (np.arange(l) for l in shape)
        # Grids (can numpy fix meshgrid typing ....)
        G = np.meshgrid(*R)  # type: ignore
        # Unraveled
        U = tuple(np.ravel(i) for i in G)
        # Joined
        return np.vstack(U).astype(np.int64)

    def point(x: float, y: float, z: float):
        return np.array([x, y, z], dtype=np.float64)

    def fix_point(p: V):
        return _.point(*p)

    def row_dot(P: Array[F], p: Array[F]) -> Array[F]:
        """ Row-wise dot product """
        return np.einsum('ij,i->j', P, p)  # type: ignore

    def sqr_norm(P: Array[F]) -> Array[F]:
        return np.sum(P * P, axis=0)

    def dbg(**vars: Array[F | B | I]):
        for k, v in vars.items():
            print(k, v.shape)

    def is_point(P: Array[F]):
        return P.shape == (3,)

    def is_points(P: Array[F]):
        return len(P.shape) == 2 and P.shape[0] == 3

    def less(P: Array[F], W: float) -> Array[B]:
        return P < W  # type: ignore


class Field:
    """ Abstract Base field """

    def field(self, P: Array[F]) -> Array[F]: ...

    def compute(self, shape: int3, matrix: glm.mat4, width: float):
        # Centered coords
        C = _.coords(*shape) + 0.5
        # Inverse affine matrix
        T = mat.to_affine(glm.affineInverse(matrix))
        # mat3
        M = T[:, :3]
        # vec3
        V = T[:, 3:]
        # Transform coords
        P = (M @ C) + V
        # Get distance field
        D = self.field(P)
        # To voxel grid
        G = _.less(D, width * width).reshape(shape)
        # FIXME (why is this needed ...)
        return G.swapaxes(0, 1)


class Sphere(Field):

    def __init__(self, center: _.V = glm.vec3()):
        self.center = _.fix_point(center)

    def __post_init__(self):
        assert _.is_point(self.center), "{center} is not a point"

    def field(self, P: Array[F]) -> Array[F]:
        assert _.is_points(P), "{P} is not array of points"
        # Compute distance field
        return _.sqr_norm(P - self.center[:, _.ex])


class Cylinder(Field):
    def __init__(self, a: _.V, b: _.V):
        self.a = _.fix_point(a)
        self.b = _.fix_point(b)

    def field(self, P: Array[F]) -> Array[F]:
        assert _.is_points(P), "{P} is not array of points"
        # Relative vectors
        pa = P - self.a[:, _.ex]
        ba = self.b - self.a
        # Projection
        proj = _.row_dot(pa, ba) / np.dot(ba, ba)
        # Compute distance field
        D = _.sqr_norm(pa - ba[:, _.ex] * proj[_.ex, :])
        # Cut ends
        D[(0.0 > proj) | (proj > 1.0)] = np.inf
        # done
        return D


class Capsule(Field):
    def __init__(self, a: _.V, b: _.V):
        self.a = _.fix_point(a)
        self.b = _.fix_point(b)

    def field(self, P: Array[F]) -> Array[F]:
        assert _.is_points(P), "{P} is not array of points"
        # Relative vectors
        pa = P - self.a[:, _.ex]
        ba = self.b - self.a
        # Projection
        proj = _.row_dot(pa, ba) / np.dot(ba, ba)
        # Clamp to ends
        ends = np.clip(proj, 0.0, 1.0)  # type: ignore
        # Compute distance field
        return _.sqr_norm(pa - ba[:, _.ex] * ends[_.ex, :])


if __name__ == '__main__':
    def test(f: Field):
        G = f.compute((10, 10, 10), glm.mat4(), 2.5)
        N = f.__class__.__name__
        print(N, G.mean())


    test(Sphere(_.point(5, 5, 5)))
    test(Cylinder(_.point(3, 3, 3), _.point(7, 7, 7)))
    test(Capsule(_.point(3, 3, 3), _.point(7, 7, 7)))
