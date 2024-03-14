import numpy as np

# Holds ray data
class ray():
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def at_t(self, t):
        return self.origin + t * self.direction


# Each hit produces a record
class hit_record():
    def __init__(self):
        self.p = None
        self.normal = None
        self.t = None
        self.front_face = None
        self.mat = None

        self.scattered = None
        self.attenuation = None

    def set_face_normal(self, r, outward_normal):
        self.front_face = (np.dot(r.direction, outward_normal) < 0)
        if self.front_face:
            self.normal = outward_normal
        else:
            self.normal = -outward_normal

# Helper functions
class interval():
    def __init__(self, mine=np.inf, maxe=-np.inf):
        self.min = mine
        self.max = maxe

    def contains(self, x):
        return (self.min <= x) and (x <= self.max)

    def surrounds(self, x):
        return (self.min < x) and (x < self.max)

    def clamp(self, x):
        if x <= self.min: return self.min
        if x >= self.max: return self.max

    def expand(self, delta):
        padding = delta/2
        return interval(self.min - padding, self.max + padding)
