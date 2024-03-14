from ray import interval

class hittable_list():
    def __init__(self):
        self.hittable_list = []
        self.bbox = None

    def clear(self):
        self.hittable_list = []

    def add(self, object):
        self.hittable_list.append(object)
        # self.bbox = aabb(self.bbox, self.bounding_box())

    def bounding_box(self):
        return self.bbox

    def hit(self, r, ray_t, rec):
        temp_rec = rec
        hit_anything = False
        closest_so_far = ray_t.max

        for object in self.hittable_list:
            if object.hit(r, interval(ray_t.min, closest_so_far), rec):
                hit_anything = True
                closest_so_far = temp_rec.t
                rec = temp_rec

        return hit_anything

# Not implemented. And no need to implement. Python hass efficient Trees.


'''
class aabb():
    def __init__(self, a, b):
        self.x = interval((min(a[0], b[0])), (max(a[0], b[0])))
        self.y = interval((min(a[1], b[1])), (max(a[1], b[1])))
        self.z = interval((min(a[2], b[2])), (max(a[2], b[2])))

    def pad(self,):
        delta = 0.0001
        if self.x.size() >= delta: new_x = self.x
        else: new_x = self.x.expand(delta)
        if self.y.size() >= delta: new_y = self.y
        else: new_y = self.y.expand(delta)
        if self.z.size() >= delta: new_z = self.z
        else: new_z = self.z.expand(delta)

        return aabb(new_x, new_y, new_z)

    def axis(self, a):
        if a == 1: return self.y
        if a == 2: return self.z
        return self.x

    def hit(self, r, ray_t):
        for _ in r:
            invD = 1 / r.direction[_]
            orig = r.origin[_]
            t0 = (self.axis(_).min - orig) * invD
            t1 = (self.axis(_).max - orig) * invD

            if invD < 0: np.swap(t0, t1)

            if t0 > ray_t.min: ray_t.min = t0
            if t1 < ray_t.max: ray_t.max = t1

            if ray_t.max <= ray_t.min: return False

        return True

    def surrounding_box(self, box0, box1):
        small = np.array((min(box0.x.min, box1.x.min),
                        min(box0.y.min, box1.y.min),
                        min(box0.z.min, box1.z.min)))
        big = np.array((max(box0.x.max, box1.x.max),
                        max(box0.y.max, box1.y.max),
                        min(box0.z.max, box1.z.max)))
        return(small, big)

class bvh_node():
    def __init__(self, src_objects):
        self.left = None
        self.right = None
        self.bbox = None

    def hit(self, r, ray_t, rec):
        if not self.bbox.hit(r, ray_t):
            return False

        hit_left = self.left.hit(r, ray_t, rec)
        if hit_left:
            m = rec.t
        else:
            m = ray_t.max
        hit_right = self.right.hit(r, interval(ray_t.min, m), rec)

        return hit_left or hit_right

    def bounding_box(self): return self.bbox

    def box_compare(self, a, b, axis_index):
        return a.bounding_box().axis(axis_index).min < b.bounding_box().axis(axis_index).min

    def box_x_compare (self, a, b):
        return self.box_compare(a, b, 0)

    def box_y_compare (self, a, b):
        return self.box_compare(a, b, 1)

    def box_z_compare (self, a, b):
        return self.box_compare(a, b, 2)
'''
