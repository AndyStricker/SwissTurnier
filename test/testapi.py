import unittest
import json
import swissturnier.api

try:
    import paste
    import paste.fixture
except ImportError:
    paste = None

class TestAPI(unittest.TestCase):
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

    @unittest.skipIf(paste is None, "Requires paste library")
    def test_playrounds(self):
        r = self.test_app.get('/v1/playround/0')
        self.assertEqual(r.status, 200)
        data = json.JSONDecoder().decode(r.body.decode('UTF-8'))
        self.assertEqual(data['count'], 0)
        self.assertIsInstance(data['plays'], list)

        r = self.test_app.get('/v1/playround/1')
        self.assertEqual(r.status, 200)
        data = json.JSONDecoder().decode(r.body.decode('UTF-8'))
        self.assertGreaterEqual(data['count'], 1)
        self.assertIsInstance(data['plays'], list)
        play = data['plays'][0]
        self.assertEqual(play['round_number'], 1)

        url = play['_links']['self']['href']

        r = self.test_app.get(url)
        self.assertEqual(r.status, 200)
        data = json.JSONDecoder().decode(r.body.decode('UTF-8'))
        self.assertEqual(play['id_playround'], data['id_playround'])
        self.assertEqual(play['round_number'], data['round_number'])
        self.assertEqual(play['id_team_a'], data['id_team_a'])
        self.assertEqual(play['id_team_b'], data['id_team_b'])
        self.assertEqual(play['points_a'], data['points_a'])
        self.assertEqual(play['points_b'], data['points_b'])

