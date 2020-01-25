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

class Turnier(object):
    """ Encapsulate the turnier logic """
    def __init__(self, db):
        self._db = db

    @property
    def db(self):
        return self._db

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
        if points_a == points_b:
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
            ranks = session.query(Rankings).order_by('rank').all()
            # check for byes
            byeplay = None
            if len(ranks) % 2 != 0:
                team_a = self._find_bye_candidates(session, ranks)
                byeplay = PlayRound(
                    round_number=(current_round + 1),
                    id_team_a=team_a.id_team,
                    id_team_b=None
                )

            while len(ranks) > 1:
                team_a = ranks.pop(0)
                team_b = self._find_new_pairing(session, ranks, team_a)
                play = PlayRound(
                    round_number=(current_round + 1),
                    id_team_a=team_a.id_team,
                    id_team_b=team_b.id_team
                )
                session.add(play)

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
