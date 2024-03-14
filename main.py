import numpy as np
import multiprocessing
from tree import hittable_list

from material import diffuse_light, lambertian, dielectric, metal
from ray import ray, hit_record, interval
from hittable import sphere

from tqdm import tqdm

class Build():
    def __init__(self, size):
        # Place the items in the world
        self.world = hittable_list()

        self.material_ground = lambertian((0.8, 0.8, 0.0))
        self.world.add(sphere((0, -100, -1), 99.5, self.material_ground))

        self.diff_light = diffuse_light((1, 1, 1))
        self.world.add(sphere((0, 1.5, 0.5), 0.5, self.diff_light))

        self.material_center = lambertian((0.1, 0.2, 0.5))
        self.material_left = dielectric(1.5)
        self.material_right = metal((0.8, 0.6, 0.2), 0.0)

        self.sphere = sphere((0, 0, 0), 0.5, self.material_center)
        self.sphere1 = sphere((-1, 0, 0), 0.5, self.material_left)
        self.sphere2 = sphere((1, 0, 0), 0.5, self.material_right)
        self.world.add(self.sphere)
        self.world.add(self.sphere1)
        self.world.add(self.sphere2)

        self.cam = camera(size[1], 16.0/9.0)
        self.image = self.cam.render_mp(self.world)

'''
        self.material_ground = lambertian((0.5, 0.5, 0.5))
        self.world.add(sphere((0,-1000,0), 1000, self.material_ground))

        for a in range(-11,12):
            for b in range(-11,12):
                choose_mat = np.random.uniform()
                center = np.array((a + 0.9*np.random.uniform(), 0.2, b + 0.9*np.random.uniform()))

                if np.linalg.norm(center - np.array((4, 0.2, 0))) > 0.9:
                    if (choose_mat < 0.8):
                        albedo = np.random.uniform(size=3) * np.random.uniform(size=3)
                        sphere_material = lambertian(albedo)
                        self.world.add(sphere(center, 0.2, sphere_material))
                    elif (choose_mat < 0.95):
                        albedo = np.random.uniform(size=3)
                        fuzz = np.random.uniform(0,0.5)
                        sphere_material = metal(albedo, fuzz)
                        self.world.add(sphere(center, 0.2, sphere_material))
                    else:
                        sphere_material = dielectric(1.5)
                        self.world.add(sphere(center, 0.2, sphere_material))

        material1 = dielectric(1.5);
        self.world.add(sphere((0, 1, 0), 1.0, material1))

        material2 = lambertian((0.4, 0.2, 0.1))
        self.world.add(sphere((-4, 1, 0), 1.0, material2))

        material3 = metal((0.7, 0.6, 0.5), 0.0)
        self.world.add(sphere((4, 1, 0), 1.0, material3))
'''

class camera():
    def __init__(self, height, aspect_ratio):
        # Camera, vieport setup etc.
        self.aspect_ratio = aspect_ratio
        self.image_height = height
        self.image_width = int(self.image_height * self.aspect_ratio)
        self.image = np.zeros((self.image_height, self.image_width, 3))

        self.samples_per_pixel = 50
        self.max_depth = 10
        self.gamma = 2

        theta = np.pi/2
        self.look_from = np.array((0, 0, 1))
        self.look_at = np.array((0, 0, -1))
        self.vup = np.array((0, 1, 0))

        self.focal_length = np.linalg.norm(self.look_from - self.look_at)

        h = np.tan(theta/2)
        self.viewport_height = 2.0 * h * self.focal_length
        self.viewport_width = self.viewport_height * self.aspect_ratio

        self.w = (self.look_from - self.look_at)/np.linalg.norm(self.look_from - self.look_at)
        self.u = np.cross(self.vup, self.w)/np.linalg.norm(np.cross(self.vup, self.w))
        self.v = np.cross(self.w, self.u)

        self.viewport_coord_arr = np.zeros((self.image_height, self.image_width, 3))

        self.set_viewport_coord()

    def set_viewport_coord(self):
        viewport_u = self.viewport_width * self.u
        viewport_v = -self.viewport_height * self.v
        self.pixel_delta_u = viewport_u / self.image_width
        self.pixel_delta_v = viewport_v / self.image_height

        viewport_upper_left = self.look_from - self.focal_length * self.w - viewport_u/2 - viewport_v/2
        self.pixel00_loc = viewport_upper_left + 0.5 * (self.pixel_delta_u + self.pixel_delta_v)

    # This is the main loop that deals with rays
    def ray_color(self, r, depth, world):
        if depth <= 0:
            return np.array((0, 0, 0))

        self.rec = hit_record()

        if not world.hit(r, interval(0.001, np.inf), self.rec):
            unit_direction = r.direction/np.linalg.norm(r.direction)
            a = 0.5 * (unit_direction[1] + 1.0)
            return (1 - a) * np.array((1, 1, 1)) + a * np.array((0.5, 0.7, 1.0))

        color_from_emission = self.rec.mat.emit()
        if not self.rec.mat.scatter(r, self.rec):
            return color_from_emission

        scattered = self.rec.scattered
        attenuation = self.rec.attenuation
        color_from_scatter = np.array(self.ray_color(scattered, depth-1, world)) * attenuation

        return color_from_emission + color_from_scatter

    # One line per processs, generate rays from origin ang get the color
    def render_mp(self, world):
        with multiprocessing.Pool(processes=12) as pool:
            results = tqdm(pool.imap(self.render_wrapper, [(self, world, y) for y in range(0, self.image_height)]), total = self.image_height)
            results = np.array(list(results)).reshape(self.image_height, self.image_width, 3)
        self.image = results * 255
        return self.image.astype(np.uint8)

    def render_wrapper(self, arg):
        w = arg[1]
        y = arg[2]
        row = np.zeros((self.image_width, 3))
        for x in range(len(row)):
            self.viewport_coord_arr[y, x] = x*self.pixel_delta_u+y*self.pixel_delta_v + self.pixel00_loc
            for _ in range(self.samples_per_pixel):
                rnd_du = self.pixel_delta_u*[np.random.uniform()-0.5, 0, 0]
                rnd_dv = self.pixel_delta_v*[0, np.random.uniform()-0.5, 0]
                ray_direction = self.viewport_coord_arr[y, x] + rnd_du + rnd_dv - self.look_from
                r = ray(self.look_from, ray_direction)
                row[x] += (self.ray_color(r, self.max_depth, w))**(1/self.gamma)
            row[x] /= self.samples_per_pixel
        return row

# Single process rendef for debug
'''
    def render(self, world):
        for y in tqdm(range(self.image_height)):
            for x in range(self.image_width):
                self.viewport_coord_arr[y, x] = x*self.pixel_delta_u+y*self.pixel_delta_v + self.pixel00_loc
                for _ in range(self.samples_per_pixel):
                    rnd_du = self.pixel_delta_u*[np.random.uniform()-0.5, 0, 0]
                    rnd_dv = self.pixel_delta_v*[0, np.random.uniform()-0.5, 0]
                    ray_direction = self.viewport_coord_arr[y, x] + rnd_du + rnd_dv - self.look_from
                    r = ray(self.look_from, ray_direction)
                    self.image[y, x] += (self.ray_color(r, self.max_depth, world))**(1/self.gamma)
                self.image[y,x] /= self.samples_per_pixel
        self.image *= 255
        return self.image.astype(np.uint8)
'''