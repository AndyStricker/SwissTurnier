import unittest
import json
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
    def test_api_index(self):
        r = self.test_app.get('/', headers={'Accept': 'text/html'})
        self.assertEqual(r.status, 200)
        r.mustcontain('<!DOCTYPE html>')
        r.mustcontain('<title>Teams</title>')

    @unittest.skipIf(paste is None, "Requires paste library")
    def test_api_categories(self):
        r = self.test_app.get('/v1/categories', headers={'Accept': 'application/json'})
        self.assertEqual(r.status, 200)
        data = json.JSONDecoder().decode(r.body.decode('UTF-8'))
        self.assertIsInstance(data['count'], int)
