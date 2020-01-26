import unittest
import swissturnier.db
import swissturnier.ranking
import sqlalchemy

class TestDB(unittest.TestCase):
    def setUp(self):
        self._setupdb()
        self._insert_categories()

    def _setupdb(self):
        self.db = swissturnier.db.DB(config={'schema': 'sqlite'})
        # Create a memory DB
        self.db._engine = sqlalchemy.create_engine('sqlite://')
        self.db.createdb()

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

    def test_turnier_init(self):
        teams = ['Duo A', 'Duo B', 'Duo C', 'Duo D']
        self._insert_teams('Mixed', teams)
        turnier = swissturnier.ranking.Turnier(self.db)
        turnier.init_rankings()
        with self.db.session_scope() as session:
            rcount = session.query(swissturnier.db.Rankings).count()
            self.assertEqual(rcount, len(teams))

    def _get_playtable(self):
        with self.db.session_scope() as session:
            plays = session.query(swissturnier.db.PlayRound).all()
            return [(
                play.team_a.name,
                play.team_b.name if play.team_b is not None else 'bye',
                play.points_a,
                play.points_b,
                ) for play in plays]

    def test_turnier_initial_next_round(self):
        teams = ['Duo A', 'Duo B', 'Duo C', 'Duo D']
        self._insert_teams('Mixed', teams)
        turnier = swissturnier.ranking.Turnier(self.db)
        turnier.init_rankings()
        turnier.next_round()

        playtable = self._get_playtable()
        self.assertEqual(playtable, [
            ('Duo A', 'Duo B', None, None),
            ('Duo C', 'Duo D', None, None),
        ])

    def test_turnier_next_round(self):
        teams = ['Duo A', 'Duo B', 'Duo C', 'Duo D']
        self._insert_teams('Mixed', teams)
        turnier = swissturnier.ranking.Turnier(self.db)
        turnier.init_rankings()

        turnier.next_round()
        with self.db.session_scope() as session:
            plays = session.query(swissturnier.db.PlayRound).all()
            plays[0].points_a = 5
            plays[0].points_b = 10
            plays[1].points_a = 16
            plays[1].points_b = 16

        turnier.next_round()
        playtable = self._get_playtable()
        self.assertEqual(playtable, [
            ('Duo A', 'Duo B', 5, 10),
            ('Duo C', 'Duo D', 16, 16),
            ('Duo B', 'Duo C', None, None),
            ('Duo D', 'Duo A', None, None),
        ])

    def _get_ranktable(self):
        with self.db.session_scope() as session:
            ranks = session.query(swissturnier.db.Rankings).order_by('rank').all()
            return [(
                rank.rank, rank.team.name, rank.wins, rank.points
                ) for rank in ranks]

    def test_turnier_ranktable(self):
        teams = ['Duo A', 'Duo B', 'Duo C', 'Duo D']
        self._insert_teams('Mixed', teams)
        turnier = swissturnier.ranking.Turnier(self.db)
        turnier.init_rankings()

        turnier.next_round()
        with self.db.session_scope() as session:
            plays = session.query(swissturnier.db.PlayRound).all()
            plays[0].points_a = 5
            plays[0].points_b = 10
            plays[1].points_a = 16
            plays[1].points_b = 16

        turnier.next_round()

        ranktable = self._get_ranktable()
        self.assertEqual(ranktable, [
            (1, 'Duo B', 1, 10),
            (2, 'Duo C', 0.5, 16),
            (3, 'Duo D', 0.5, 16),
            (4, 'Duo A', 0, 5),
        ])

    def test_turnier4(self):
        teams = ['Duo A', 'Duo B', 'Duo C', 'Duo D']
        self._insert_teams('Mixed', teams)
        turnier = swissturnier.ranking.Turnier(self.db)
        turnier.init_rankings()
        turnier.next_round()

        with self.db.session_scope() as session:
            plays = session.query(swissturnier.db.PlayRound).all()
            plays[0].points_a = 5
            plays[0].points_b = 10
            plays[1].points_a = 16
            plays[1].points_b = 16

        turnier.next_round()

        playtable = self._get_playtable()
        self.assertEqual(playtable, [
            ('Duo A', 'Duo B', 5, 10),
            ('Duo C', 'Duo D', 16, 16),
            ('Duo B', 'Duo C', None, None),
            ('Duo D', 'Duo A', None, None),
        ])
        ranktable = self._get_ranktable()
        self.assertEqual(ranktable, [
            (1, 'Duo B', 1, 10),
            (2, 'Duo C', 0.5, 16),
            (3, 'Duo D', 0.5, 16),
            (4, 'Duo A', 0, 5),
        ])

        with self.db.session_scope() as session:
            plays = session.query(swissturnier.db.PlayRound).all()
            plays[2].points_a = 20
            plays[2].points_b = 15
            plays[3].points_a = 16
            plays[3].points_b = 14

        turnier.next_round()

        ranktable = self._get_ranktable()
        self.assertEqual(ranktable, [
            (1, 'Duo B', 2, 30),
            (2, 'Duo D', 1.5, 32),
            (3, 'Duo C', 0.5, 31),
            (4, 'Duo A', 0, 19),
        ])
        playtable = self._get_playtable()
        self.assertEqual(playtable, [
            ('Duo A', 'Duo B', 5, 10),
            ('Duo C', 'Duo D', 16, 16),
            ('Duo B', 'Duo C', 20, 15),
            ('Duo D', 'Duo A', 16, 14),
            ('Duo B', 'Duo D', None, None),
            ('Duo C', 'Duo A', None, None),
        ])

        with self.db.session_scope() as session:
            plays = session.query(swissturnier.db.PlayRound).all()
            plays[4].points_a = 17
            plays[4].points_b = 19
            plays[5].points_a = 18
            plays[5].points_b = 12

        turnier.rank()

        ranktable = self._get_ranktable()
        self.assertEqual(ranktable, [
            (1, 'Duo D', 2.5, 51),
            (2, 'Duo B', 2, 47),
            (3, 'Duo C', 1.5, 49),
            (4, 'Duo A', 0, 31),
        ])
        playtable = self._get_playtable()
        self.assertEqual(playtable, [
            ('Duo A', 'Duo B', 5, 10),
            ('Duo C', 'Duo D', 16, 16),
            ('Duo B', 'Duo C', 20, 15),
            ('Duo D', 'Duo A', 16, 14),
            ('Duo B', 'Duo D', 17, 19),
            ('Duo C', 'Duo A', 18, 12),
        ])

    def test_turnier_byes3(self):
        teams = ['Team A', 'Team B', 'Team C']
        self._insert_teams('Male', teams)
        turnier = swissturnier.ranking.Turnier(self.db)
        turnier.init_rankings()
        turnier.next_round()

        playtable = self._get_playtable()
        self.assertEqual(playtable, [
            ('Team A', 'Team B', None, None),
            ('Team C', 'bye', 10, None),
        ])

        with self.db.session_scope() as session:
            plays = session.query(swissturnier.db.PlayRound).all()
            plays[0].points_a = 20
            plays[0].points_b = 11

        turnier.next_round()

        ranktable = self._get_ranktable()
        self.assertEqual(ranktable, [
            (1, 'Team A', 1, 20),
            (2, 'Team C', 1, 10),
            (3, 'Team B', 0, 11),
        ])

        playtable = self._get_playtable()
        self.assertEqual(playtable, [
            ('Team A', 'Team B', 20, 11),
            ('Team C', 'bye', 10, None),
            ('Team A', 'Team C', None, None),
            ('Team B', 'bye', 10, None),
        ])

        with self.db.session_scope() as session:
            plays = session.query(swissturnier.db.PlayRound).all()
            plays[2].points_a = 17
            plays[2].points_b = 23

        turnier.rank()

        playtable = self._get_playtable()
        self.assertEqual(playtable, [
            ('Team A', 'Team B', 20, 11),
            ('Team C', 'bye', 10, None),
            ('Team A', 'Team C', 17, 23),
            ('Team B', 'bye', 10, None),
        ])
        ranktable = self._get_ranktable()
        self.assertEqual(ranktable, [
            (1, 'Team C', 2, 33),
            (2, 'Team A', 1, 37),
            (3, 'Team B', 1, 21),
        ])
