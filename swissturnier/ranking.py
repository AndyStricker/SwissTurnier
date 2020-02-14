# -*- coding: utf-8 -*-
# Copyright © 2020 Andreas Stricker <andy@knitter.ch>
# 
# This file is part of SwissTurnier.
# 
# SwissTurnier is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sqlalchemy
import swissturnier.db
from swissturnier.db import Category, Team, PlayRound, Rankings
import math

class Turnier(object):
    """ Encapsulate the turnier logic """

    # How many points teams gets strongly depends on the play duration
    # On average it's 17 and the median is 18. But when looking at
    # winners it's 21 and for loosers it's 13. It seems reasonable to
    # give at least 10 points up to 17 at most for a bye.
    BYE_PLAY_POINTS = 10

    def __init__(self, db):
        self._db = db

    @property
    def db(self):
        return self._db

    @property
    def play_settings(self):
        return self.db.config.play_settings

    def init_rankings(self):
        """ Initially clear and regenerate the rankings table """
        with self.db.session_scope() as session:
            session.query(Rankings).delete()
            teams = session.query(Team).all()
            # Of course a SQL query can also do this
            for team in teams:
                r = Rankings(
                    id_team=team.id_team,
                    wins=0,
                    points=0,
                )
                session.add(r)

    def next_round(self):
        """
        Calculate rankings until current round and then build the next
        round play table.
        """
        self.rank()
        self.generate_round_playplan()

    def rank(self, to_round=None):
        """ Calculate rankings until current round """
        with self.db.session_scope() as session:
            round_count = session.query(PlayRound).distinct(PlayRound.round_number).count()
            if round_count == 0:
                return  # no plays yet, nothing to calculate

            if to_round is None or to_round == 0:
                # rank all plays
                current_round = swissturnier.db.query_current_round(session)
            else:
                current_round = to_round

            # reset wins and points to zero
            ranks = session.query(Rankings).update({
                'wins': 0,
                'points': 0,
            })

            for play_round in range(1, current_round + 1):
                plays = session.query(PlayRound).filter_by(round_number=play_round).all()
                for play in plays:
                    wins_a, wins_b = self._team_play_wins(play.points_a, play.points_b)

                    rank_a = session.query(Rankings).filter_by(id_team=play.id_team_a).one()
                    rank_a.points += play.points_a
                    rank_a.wins += wins_a

                    if play.id_team_b is None:  # byes
                        continue
                    rank_b = session.query(Rankings).filter_by(id_team=play.id_team_b).one()
                    rank_b.points += play.points_b
                    rank_b.wins += wins_b
            # sort by wins, then by points
            for num, rank in enumerate(session.query(Rankings).order_by(sqlalchemy.desc('wins'), sqlalchemy.desc('points')).all()):
                rank.rank = num + 1

    def _team_play_wins(self, points_a, points_b):
        """ Winning a game get one point, drawn get a half point """
        if points_b is None:  # bye
            return (1.0, 0.0)
        elif points_a == points_b:
            return (0.5, 0.5)
        elif points_a > points_b:
            return (1.0, 0.0)
        else:
            return (0.0, 1.0)

    def check_complete(self, to_round):
        with self.db.session_scope() as session:
            missing_a = session.query(PlayRound).filter_by(points_a=None).count()
            missing_b = session.query(PlayRound).filter_by(points_b=None).count()
            return (missing_a == 0 or missing_b <= 1)

    def generate_round_playplan(self):
        """ Assing teams for the next round of play """
        with self.db.session_scope() as session:
            current_round = swissturnier.db.query_current_round(session)
            team_count = swissturnier.db.query_team_count(session)

            ranks = session.query(Rankings).order_by('rank').all()
            # check for byes
            byeplay = None
            if len(ranks) % 2 != 0:
                team_a = self._find_bye_candidates(session, ranks)
                byeplay = PlayRound(
                    round_number=(current_round + 1),
                    id_team_a=team_a.id_team,
                    id_team_b=None,
                    points_a = self.BYE_PLAY_POINTS
                )

            round_nth_play = 1
            while len(ranks) > 1:
                team_a = ranks.pop(0)
                team_b = self._find_new_pairing(session, ranks, team_a)
                start_time = self._calculate_play_starttime(
                    current_round,
                    round_nth_play,
                    team_count
                )
                play = PlayRound(
                    round_number=(current_round + 1),
                    id_team_a=team_a.id_team,
                    id_team_b=team_b.id_team,
                    start_time=start_time,
                    court=self._assign_court(round_nth_play)
                )
                session.add(play)
                round_nth_play += 1

            if not byeplay is None:
                session.add(byeplay)

    def _find_bye_candidates(self, session, ranks):
        index = len(ranks) - 1
        while index > 0:
            count = self._query_byes_by_team(session, ranks[index].team)
            if count == 0:
                break
            index -= 1
        else:
            raise Exception("Couldn't find a team without a bye")
        return ranks.pop(index)

    def _query_byes_by_team(self, session, team):
        """ Query byes played by a given team """
        return (session.query(PlayRound)
            .filter_by(id_team_a=team.id_team)
            .filter_by(id_team_b=None)
            .count())

    def _find_new_pairing(self, session, ranks, team):
        """ find another team which has not played with this team before """
        idx = 0
        while self._has_former_pairing(session, team, ranks[idx]):
            idx += 1
        return ranks.pop(idx)

    def _has_former_pairing(self, session, team1, team2):
        """ check if two teams have already played against before """
        return (session.query(PlayRound)
            .filter(
                sqlalchemy.or_(
                    sqlalchemy.and_(
                        PlayRound.id_team_a == team1.id_team,
                        PlayRound.id_team_b == team2.id_team),
                    sqlalchemy.and_(
                        PlayRound.id_team_a == team2.id_team,
                        PlayRound.id_team_b == team1.id_team)
                )
            ).count() > 0)

    def _calculate_play_starttime(self, current_round, round_nth_play, team_count):
        start_time = self.play_settings.start_time
        play_time = self.play_settings.play_time
        rotation_time = self.play_settings.rotation_time
        pause_time = self.play_settings.pause_time
        courts = self.play_settings.courts

        # team_count halved equals the pairings and therefore plays.
        # Divided by courts we have the number of plays for each round
        # that are not at the same time:
        round_timeslots = int(math.ceil(math.floor(team_count / 2.0) / courts))
        # Each round duration is the play time plus rotation time times
        # the number of time slots:
        round_time = round_timeslots * (play_time + rotation_time) + pause_time
        # Once we know the round time we are able to calculate the time
        # a round starts:
        round_start_time = start_time + current_round * round_time
        # With all above we can calculate the start time of the play:
        play_start_time = round_start_time + math.floor(float(round_nth_play - 1) / courts) * (play_time + rotation_time)

        return play_start_time

    def _assign_court(self, round_nth_play):
        courts = self.play_settings.courts
        court_number = (round_nth_play - 1) % courts
        return chr(ord('A') + court_number)
