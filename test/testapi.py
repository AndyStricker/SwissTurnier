import unittest
import swissturnier.api

try:
    import paste
    import paste.fixture
except ImportError:
    paste = None

class TestDB(unittest.TestCase):
    def setUp(self):
        app = swissturnier.api.get_application()
        self.middleware = []
        self.test_app = paste.fixture.TestApp(app.wsgifunc(*self.middleware))

    def tearDown(self):
        self.middleware = None
        self.test_app = None

    @unittest.skipIf(paste is None, "Requires paste library")
    def test_api(self):
        req = self.test_app.get('/', headers={'Content-Type': 'application/json'})
        self.assertEqual(req.status, 200)

