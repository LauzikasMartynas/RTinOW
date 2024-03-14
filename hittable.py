import numpy as np
from abc import ABC, abstractmethod

from ray import hit_record, interval

class hittable(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def hit(self, r, ray_t, rec):
        pass

# Converts e.g. sphere to "smoky" sphere
class constant_medium(hittable):
    def __init__(self, object, D, mat):
        self.object = object
        self.neg_inv_density = -1/D

    def hit(self, r, ray_t, rec):
        self.rec1 = hit_record()
        self.rec2 = hit_record()

        if not self.object.hit(r, interval(-np.inf, np.inf), self.rec1):
            return False

        if not self.object.hit(r, interval(self.rec1.t + 0.0001, np.inf), self.rec2):
            return False

        if self.rec1.t < ray_t.min:
            self.rec1.t = ray_t.min

        if self.rec2.t > ray_t.max:
            self.rec2.t = ray_t.max

        if self.rec1.t >= self.rec2.t:
            return False

        if self.rec1.t < 0:
            self.rec1.t = 0

        ray_length = np.linalg.norm(r.direction)
        distance_inside_boundary = (self.rec2.t - self.rec1.t) * ray_length
        hit_distance = self.neg_inv_density * np.log(np.random.uniform())

        if hit_distance > distance_inside_boundary:
            return False

        rec.t = self.rec1.t + hit_distance / ray_length
        rec.p = r.at_t(rec.t)

        rec.normal = (1, 0, 0)
        rec.front_face = True
        rec.mat = self.object.mat

        return True


class sphere(hittable):
    def __init__(self, center, radius, mat):
        self.center = np.array(center)
        self.radius = radius
        self.mat = mat
        # self.bbox = aabb(self.center - self.radius, self.center + self.radius)

    def hit(self, r, ray_t, rec):
        oc = r.origin - self.center
        a = np.dot(r.direction, r.direction)
        half_b = np.dot(oc, r.direction)
        c = np.dot(oc, oc) - self.radius**2

        discriminant = half_b**2 - a*c
        if (discriminant < 0):
            return False

        sqrtd = np.sqrt(discriminant)
        root = (-half_b - sqrtd) / a
        if (not ray_t.surrounds(root)):
            root = (-half_b + sqrtd) / a
            if (not ray_t.surrounds(root)):
                return False

        rec.t = root
        rec.p = r.at_t(rec.t)
        outward_normal = (rec.p - self.center) / self.radius
        rec.set_face_normal(r, outward_normal)
        rec.mat = self.mat

        return True

# Not tested
class quad(hittable):
    def __init__(self, Q, U, V, mat):
        self.Q = Q
        self.u = U
        self.v = V
        self.n = np.cross(self.u, self.v)
        self.mat = mat
        self.normal = np.cross(self.u, self.v)
        self.D = np.dot(self.normal, self.Q)
        self.W = self.normal / np.dot(self.n, self.n)

    def hit(self, r, ray_t, rec):
        denom = np.dot(self.normal, r.direction)
        if abs(denom) < 1e-8:
            return False

        t = (self.D - np.dot(self.normal, r.origin))/denom
        if not ray_t.contains(t):
            return False

        intersection = r.ar_t(t)
        planar_hitpt_vector = intersection - self.Q
        alpha = np.dot(self.w, np.cross(planar_hitpt_vector, v))
        beta = np.dot(self.w, np.cross(self.u, planar_hitpt_vector))

        if not is_interior(alpha, beta, parent.rec):
            return False

        parent.rec.t = t
        parent.rec.p = intersection
        parent.rec.mat = self.mat
        parent.rec.set_face_normal(r, self.normal)

        return True

    @staticmethod
    def is_interior(a, b, rec):
        if ((a < 0) or (1 < a) or (b < 0) or (1 < b)):
            return False
        rec.u = a
        rec.v = b
        return True
