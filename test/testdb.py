import unittest
import swissturnier.db
import sqlalchemy

class TestDB(unittest.TestCase):
    def setUp(self):
        self.db = swissturnier.db.DB(config={'schema': 'sqlite'})
        # Create a memory DB
        self.db._engine = sqlalchemy.create_engine('sqlite://')
        self.db.createdb()

    def tearDown(self):
        self.db.close()

    def _insert_categories(self):
        with self.db.session_scope() as session:
            mixed = swissturnier.db.Category(name = 'Mixed')
            session.add(mixed)
            female = swissturnier.db.Category(name = 'Female')
            session.add(female)
            male = swissturnier.db.Category(name = 'Male')
            session.add(male)

    def _insert_teams(self, category, team_list):
        with self.db.session_scope() as session:
            cat = session.query(swissturnier.db.Category).filter_by(name=category).one()
            for team in team_list:
                session.add(swissturnier.db.Team(name=team, id_category=cat.id_category))
        
    def test_constructor(self):
        db = swissturnier.db.DB()
        self.assertIsInstance(db, swissturnier.db.DB)

    def test_relations(self):
        c = swissturnier.db.Category()
        t = swissturnier.db.Team()
        p = swissturnier.db.PlayRound()
        r = swissturnier.db.Rankings()

    def test_session(self):
        session = self.db.create_session()
        self.assertIsInstance(session, sqlalchemy.orm.session.Session)

    def test_teams(self):
        self._insert_categories()
        self._insert_teams('Mixed', ['Duo A', 'Duo B', 'Duo C', 'Duo D'])
        with self.db.session_scope() as session:
            team = session.query(swissturnier.db.Team).filter_by(name='Duo C').one()
            self.assertEqual(team.name, 'Duo C')
            self.assertEqual(team.category.name, 'Mixed')


if __name__ == '__main__':
    unittest.main()
