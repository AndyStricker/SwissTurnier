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

import os
import Cheetah.Template
import sqlalchemy
import swissturnier.db
from swissturnier.db import PlayRound, Rankings

class Report(object):
    def __init__(self, db):
        self._db = db

    @property
    def db(self):
        return self._db


class ConsoleRankingTableReport(Report):
    def print(self, output):
        with self.db.session_scope() as session:
            current_round = swissturnier.db.query_current_round(session)
            output.write('Current round: {}\n'.format(current_round))
            ranks = session.query(Rankings).order_by('rank').all()
            output.write('Ranks: {}\n'.format(len(ranks)))
            for rank in ranks:
                output.write("{0.rank:>3} {0.wins:>2} {0.points:>4} {0.team.name}\n".format(rank))


class ConsolePlayTableReport(Report):
    def __init__(self, db):
        super(ConsolePlayTableReport, self).__init__(db)
        self._round_number = None

    @property
    def round_number(self):
        return self._round_number

    @round_number.setter
    def round_number(self, value):
        self._round_number = value

    def print(self, output):
        with self.db.session_scope() as session:
            query = session.query(PlayRound)
            if not self.round_number is None:
                query = query.filter_by(round_number=self.round_number)
            plays = query.order_by('round_number', 'id_team_a', 'id_team_b').all()
            for play in plays:
                output.write((
                        "{play.round_number:<2} "
                        "{play.id_playround:>2}."
                        " ({play.id_team_a:3}) {play.team_a.name:30}"
                        " {play.points_a!s:>3} : {play.points_b!s:<3}"
                        " ({team_b_id}) {team_b_name}"
                        "\n"
                    ).format(
                        play=play,
                        team_b_id=(0 if play.id_team_b is None else play.id_team_b),
                        team_b_name=("Bye" if play.id_team_b is None else play.team_b.name)
                    )
                )


class CheetahReport(Report):
    def __init__(self, db, path='reports/', filename='report.tmpl'):
        super(CheetahReport, self).__init__(db)
        self._path = path
        self._filename = filename

    def get_namespace(self):
        pass

    def create(self):
        with self.db.session_scope() as session:
            path = os.path.join(self._path, self._filename)
            #tmpl = open(path, 'r').read().decode('utf-8') # TODO encoding
            tmpl = open(path, 'r').read()
            ns = self.get_namespace(session)
            result = Cheetah.Template.Template(tmpl, searchList=[ns])
            return str(result)


class HTMLPlayTable(CheetahReport):
    TITLE = 'Spielplan Badmintonturnier'

    def __init__(self, db):
        super(HTMLPlayTable, self).__init__(db, filename='playtable.tmpl')

    def get_namespace(self, session):
        current_round = swissturnier.db.query_current_round(session)
        query = session.query(PlayRound)
        if not self.round_number is None:
            query = query.filter_by(round_number=self.round_number)
        plays = query.order_by('round_number', 'id_team_a', 'id_team_b').all()
        rounds = [list() for x in range(0, current_round + 1)]
        for play in plays:
            rounds[play.round_number].append(play)
        return {
            'title': self.TITLE,
            'current_round': current_round,
            'plays': plays,
            'rounds': rounds,
        }


class HTMLRankingTableReport(CheetahReport):
    TITLE = 'Rangliste Badmintonturnier'

    def __init__(self, db):
        super(HTMLRankingTableReport, self).__init__(db, filename='ranking.tmpl')

    def get_namespace(self, session):
        current_round = swissturnier.db.query_current_round(session)
        ranks = session.query(Rankings).order_by('rank').all()
        return {
            'title': self.TITLE,
            'current_round': current_round,
            'ranks': ranks,
        }
