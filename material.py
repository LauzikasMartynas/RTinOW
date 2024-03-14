import numpy as np
from abc import ABC, abstractmethod
from ray import ray


class material(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def scatter(self, r, rec):
        pass

    def emit(self):
        return np.array((0, 0, 0))


class isotropic(material):
    def __init__(self, color):
        self.color = np.array((color))

    def scatter(self, r_in, rec):
        random_vect = np.random.uniform(-1, 1, 3)
        random_norm = random_vect/np.linalg.norm(random_vect)
        rec.scattered = ray(rec.p, random_norm)
        rec.attenuation = self.color
        return True

    def emmit(self):
        return (4, 0, 0)


class diffuse_light(material):
    def __init__(self, color):
        self.color = np.array((color))

    def scatter(self, r_in, rec):
        return False

    def emit(self):
        return self.color


class lambertian(material):
    def __init__(self, albedo):
        self.albedo = albedo

    def scatter(self, r_in, rec):
        random_vect = np.random.uniform(-1,1,3)
        random_norm = random_vect/np.linalg.norm(random_vect)
        scatter_direction = rec.normal + random_norm

        if np.linalg.norm(scatter_direction) < 1e-5:
            scatter_direction = rec.normal

        rec.scattered = ray(rec.p, scatter_direction)
        rec.attenuation = self.albedo
        return True


class metal(material):
    def __init__(self, albedo, f):
        self.albedo = albedo
        self.fuzz = None
        self.set_fuzz(f)

    def scatter(self, r_in, rec):
        unit_direction = r_in.direction/np.linalg.norm(r_in.direction)
        reflected = unit_direction - 2*np.dot(unit_direction, rec.normal) * rec.normal

        random_vect = np.random.uniform(-1, 1, 3)
        random_norm = random_vect/np.linalg.norm(random_vect)

        rec.scattered = ray(rec.p, reflected + random_norm * self.fuzz)
        rec.attenuation = self.albedo

        scat = (np.dot(rec.scattered.direction, rec.normal) > 0)
        return scat

    def set_fuzz(self, f):
        if f < 1:
            self.fuzz = f
        else:
            self.fuzz = 1


class dielectric(material):
    def __init__(self, index):
        self.ir = index

    def scatter(self, r_in, rec):
        if rec.front_face:
            rr = 1/self.ir
        else:
            rr = self.ir

        unit_direction = r_in.direction/np.linalg.norm(r_in.direction)
        n_r = np.dot(rec.normal, unit_direction)

        cos_theta = min(-n_r, 1.0)
        sin_theta = np.sqrt(1.0 - cos_theta * cos_theta)
        cannot_refract = ((rr * sin_theta) > 1.0)

        if cannot_refract or (self.reflectance(cos_theta, self.ir) > np.random.uniform()):
            direction = unit_direction - 2 * n_r * rec.normal
        else:
            dir1 = -np.sqrt(1 - rr**2 * (1-n_r**2) ) * rec.normal
            dir2 = rr*(unit_direction - n_r * rec.normal)
            direction = dir1 + dir2

        rec.scattered = ray(rec.p, direction)
        rec.attenuation = (1, 1, 1)
        return True

    @staticmethod
    def reflectance(cosine, ref_idx):
        r0 = (1-ref_idx) / (1+ref_idx)
        r0 = r0 * r0
        return r0 + (1-r0) * (1-cosine)**5
    