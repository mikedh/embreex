from unittest import TestCase
import numpy as np
from embreex import rtcore as rtc  # Use unified rtcore module
#from embreex import rtcore_scene as rtcs # Removed in Embree 4
from embreex.mesh_construction import TriangleMesh
from embreex.mesh_construction import ElementMesh


def xplane(x):
    return [
        [[x, -1.0, -1.0], [x, +1.0, -1.0], [x, -1.0, +1.0]],
        [[x, +1.0, -1.0], [x, +1.0, +1.0], [x, -1.0, +1.0]],
    ]


def xplane_only_points(x):
    # Indices are [[0, 1, 2], [1, 3, 2]]
    return [[x, -1.0, -1.0], [x, +1.0, -1.0], [x, -1.0, +1.0], [x, +1.0, +1.0]]


def define_rays_origins_and_directions():
    N = 4
    origins = np.zeros((N, 3), dtype="float32")
    origins[:, 0] = 0.1
    origins[0, 1] = -0.2
    origins[1, 1] = +0.2
    origins[2, 1] = +0.3
    origins[3, 1] = -8.2

    dirs = np.zeros((N, 3), dtype="float32")
    dirs[:, 0] = 1.0
    return origins, dirs


class Testembreex(TestCase):
    def test_embreex_should_be_able_to_display_embree_version(self):
        embreeDevice = rtc.EmbreeDevice()
        print(embreeDevice) #The repr has changed in EmbreeDevice

    def test_embreex_should_be_able_to_create_a_scene(self):
        embreeDevice = rtc.EmbreeDevice()
        rtc.EmbreeScene(embreeDevice) # Use rtcore

    def test_embreex_should_be_able_to_create_several_scenes(self):
        embreeDevice = rtc.EmbreeDevice()
        rtc.EmbreeScene(embreeDevice) # Use rtcore
        rtc.EmbreeScene(embreeDevice) # Use rtcore

    def test_embreex_should_be_able_to_create_a_device_if_not_provided(self):
        rtc.EmbreeScene() # Use rtcore


class TestIntersectionTriangles(TestCase):
    def setUp(self):
        """Initialisation"""
        triangles = xplane(7.0)
        triangles = np.array(triangles, "float32")

        self.embreeDevice = rtc.EmbreeDevice()
        self.scene = rtc.EmbreeScene(self.embreeDevice) # Use rtcore
        TriangleMesh(self.scene, triangles)

        origins, dirs = define_rays_origins_and_directions()
        self.origins = origins
        self.dirs = dirs

    def test_intersect_simple(self):
        res = self.scene.run(self.origins, self.dirs)
        self.assertTrue(np.array_equal(np.array([0, 1, 1, -1]), res)) # Use np.array_equal

    def test_intersect_distance(self):
        res = self.scene.run(self.origins, self.dirs, query="DISTANCE")
        self.assertTrue(np.allclose([6.9, 6.9, 6.9, 1e37], res))

    def test_intersect(self):
        res = self.scene.run(self.origins, self.dirs, output=True, dists=100) # output=1 -> output=True

        self.assertTrue(np.array_equal(np.array([0, 0, 0, -1]), res["geomID"])) # Use np.array_equal
        ray_inter = res["geomID"] >= 0
        primID = res["primID"][ray_inter]
        u = res["u"][ray_inter]
        v = res["v"][ray_inter]
        tfar = res["tfar"]
        self.assertTrue(np.array_equal(np.array([0, 1, 1]), primID))# Use np.array_equal
        self.assertTrue(np.allclose([6.9, 6.9, 6.9, 100], tfar))
        self.assertTrue(np.allclose([0.4, 0.1, 0.15], u))
        self.assertTrue(np.allclose([0.5, 0.4, 0.35], v))


class TestIntersectionTrianglesFromIndices(TestCase):
    def setUp(self):
        """Initialisation"""
        points = xplane_only_points(7.0)
        points = np.array(points, "float32")
        indices = np.array([[0, 1, 2], [1, 3, 2]], "uint32")

        self.embreeDevice = rtc.EmbreeDevice()
        self.scene = rtc.EmbreeScene(self.embreeDevice)  # Use rtcore
        TriangleMesh(self.scene, points, indices)

        origins, dirs = define_rays_origins_and_directions()
        self.origins = origins
        self.dirs = dirs

    def test_intersect_simple(self):
        res = self.scene.run(self.origins, self.dirs)
        self.assertTrue(np.array_equal(np.array([0, 1, 1, -1]), res)) # Use np.array_equal

    def test_intersect(self):
        res = self.scene.run(self.origins, self.dirs, output=True) # output=1 -> output=True

        self.assertTrue(np.array_equal(np.array([0, 0, 0, -1]), res["geomID"])) # Use np.array_equal

        ray_inter = res["geomID"] >= 0
        primID = res["primID"][ray_inter]
        u = res["u"][ray_inter]
        v = res["v"][ray_inter]
        tfar = res["tfar"][ray_inter]
        self.assertTrue(np.array_equal(np.array([0, 1, 1]), primID)) # Use np.array_equal
        self.assertTrue(np.allclose([6.9, 6.9, 6.9], tfar))
        self.assertTrue(np.allclose([0.4, 0.1, 0.15], u))
        self.assertTrue(np.allclose([0.5, 0.4, 0.35], v))


class TestIntersectionTetrahedron(TestCase):
    def setUp(self):
        """Initialisation"""
        vertices = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)]
        vertices = np.array(vertices, "float32")
        indices = np.array([[0, 1, 2, 3]], "uint32")
        self.embreeDevice = rtc.EmbreeDevice()
        self.scene = rtc.EmbreeScene(self.embreeDevice)  # Use rtcore
        ElementMesh(self.scene, vertices, indices)

        N = 2
        self.origins = np.zeros((N, 3), dtype="float32")
        self.origins[0, :] = (-0.1, +0.1, +0.1)
        self.origins[1, :] = (-0.1, +0.2, +0.2)
        self.dirs = np.zeros((N, 3), dtype="float32")
        self.dirs[:, 0] = 1.0

    def test_intersect_simple(self):
        res = self.scene.run(self.origins, self.dirs)
        self.assertTrue(np.array_equal(np.array([1, 1]), res)) # Use np.array_equal

    def test_intersect(self):
        res = self.scene.run(self.origins, self.dirs, output=True) # output=1 -> output=True

        self.assertTrue(np.array_equal(np.array([0, 0]), res["geomID"]))# Use np.array_equal

        ray_inter = res["geomID"] >= 0
        primID = res["primID"][ray_inter]
        u = res["u"][ray_inter]
        v = res["v"][ray_inter]
        tfar = res["tfar"][ray_inter]
        self.assertTrue(np.array_equal(np.array([0, 1]), primID)) # Use np.array_equal
        self.assertTrue(np.allclose([0.1, 0.1], tfar))
        self.assertTrue(np.allclose([0.1, 0.2], u))
        self.assertTrue(np.allclose([0.1, 0.2], v))


class TestIntersectionHexahedron(TestCase):
    def setUp(self):
        """Initialisation"""
        vertices = [
            (1.0, 0.0, 0.0),
            (1.0, 1.0, 0.0),
            (0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 1.0),
            (1.0, 1.0, 1.0),
            (0.0, 1.0, 1.0),
            (0.0, 0.0, 1.0),
        ]
        vertices = np.array(vertices, "float32")
        indices = np.array([[0, 1, 2, 3, 4, 5, 6, 7]], "uint32")
        self.embreeDevice = rtc.EmbreeDevice()
        self.scene = rtc.EmbreeScene(self.embreeDevice)  # Use rtcore
        ElementMesh(self.scene, vertices, indices)

        N = 2
        self.origins = np.zeros((N, 3), dtype="float32")
        self.origins[0, :] = (-0.1, +0.9, +0.1)
        self.origins[1, :] = (-0.1, +0.8, +0.2)
        self.dirs = np.zeros((N, 3), dtype="float32")
        self.dirs[:, 0] = 1.0

    def test_intersect_simple(self):
        res = self.scene.run(self.origins, self.dirs)
        self.assertTrue(np.array_equal(np.array([1, 1]), res)) # Use np.array_equal

    def test_intersect(self):
        res = self.scene.run(self.origins, self.dirs, output=True) # output=1 -> output=True

        self.assertTrue(np.array_equal(np.array([0, 0]), res["geomID"])) # Use np.array_equal

        ray_inter = res["geomID"] >= 0
        primID = res["primID"][ray_inter]
        u = res["u"][ray_inter]
        v = res["v"][ray_inter]
        tfar = res["tfar"][ray_inter]
        self.assertTrue(np.array_equal(np.array([0, 1]), primID)) # Use np.array_equal
        self.assertTrue(np.allclose([0.1, 0.1], tfar))
        self.assertTrue(np.allclose([0.1, 0.2], u))
        self.assertTrue(np.allclose([0.8, 0.6], v))


if __name__ == "__main__":
    from unittest import main

    main()