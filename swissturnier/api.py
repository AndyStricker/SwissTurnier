# -*- coding: utf-8 -*-
""" RESTful SwissTurnier webservice API """

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

import sys
import os
sys.path.append(os.getcwd())
import web
import web.webapi
import json
import decimal
import datetime
import sqlalchemy
import swissturnier.db
import swissturnier.ranking
import swissturnier.report

from web.contrib.template import render_cheetah
import Cheetah.Template

# RESTful API with JSON including HAL (http://stateless.co/hal_spefication.html)

PREFIX = '/v1'
urls = (
    '/', 'Index',
    PREFIX + '/ranking(/)?', 'APIv1Ranking',
    PREFIX + '/playtable(/)?', 'APIv1PlayTable',
    PREFIX + '/categories', 'APIv1Categories',
    PREFIX + '/category/(\d+)', 'APIv1Category',
    PREFIX + '/teams(/)?', 'Teams',
    PREFIX + '/team/(\d+)', 'Team',
    PREFIX + '/currentround', 'CurrentPlayRound',
    PREFIX + '/playround/(\d+)', 'PlayRounds',
    PREFIX + '/play/(\d+)', 'Play',
)

def _create_api_path(resource, *parts):
    path = [PREFIX, resource]
    path.extend([str(p) for p in parts])
    return '/'.join(path)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

api_json_encoder = JSONEncoder()


class Index:
    def GET(self):
        db = swissturnier.db.DB()
        with db.session_scope() as session:
            total_teams = session.query(swissturnier.db.Team).count()

            stats = {
                'total_teams': total_teams,
            }

            web.header('Content-Type', 'text/html')
            render = render_cheetah('reports/api')
            return render.index(title='Teams', statistics=stats)

class APIv1Ranking:
    def GET(self, slash):
        if slash:
            raise web.seeother('/ranking')

        #turnier = swissturnier.ranking.Turnier(db)
        #ranking.rank()
        db = swissturnier.db.DB()
        web.header('Content-Type', 'text/html')
        report = swissturnier.report.HTMLRankingTableReport(db)
        return report.create()

class APIv1PlayTable:
    def GET(self, slash):
        if slash:
            raise web.seeother('/playtable')

        db = swissturnier.db.DB()
        report = swissturnier.report.HTMLPlayTable(db)
        web.header('Content-Type', 'text/html')
        return report.create()

class APIv1CategoryBase(object):
    CATEGORY_ATTRIBUTES = ['id_category', 'name']
    def get_category_dict(self, category): 
        obj = {}
        for name in self.CATEGORY_ATTRIBUTES:
            obj[name] = getattr(category, name)
        obj['_links'] = {
            'self': { 'href': _create_api_path('category', obj['id_category']) },
        }
        return obj

class APIv1Categories(APIv1CategoryBase):
    def GET(self):
        db = swissturnier.db.DB()
        result = []
        with db.session_scope() as session:
            categories = session.query(swissturnier.db.Category).all()
            for category in categories:
                result.append(self.get_category_dict(category))

        web.header('Content-Type', 'application/json')
        return api_json_encoder.encode({
            'count': len(result),
            'items': result,
            '_links': {
                'self': { 'href': _create_api_path('categories') },
            },
        })

class APIv1Category(APIv1CategoryBase):
    def GET(self, id_category):
        db = swissturnier.db.DB()
        category = None
        with db.session_scope() as session:
            category = session.query(swissturnier.db.Category).get(int(id_category))
            if category is None:
                raise web.notfound(message='Category does not exist')
            obj = self.get_category_dict(category)

        web.header('Content-Type', 'application/json')
        return api_json_encoder.encode(obj)

class TeamBase(object):
    TEAM_ATTRIBUTES = ['id_team', 'name', 'category']

    def get_team_dict(self, team):
        obj = {}
        for name in self.TEAM_ATTRIBUTES:
            obj[name] = getattr(team, name)
        obj['category'] = team.category.name
        obj['_links'] = {
            'self': { 'href': _create_api_path('team', obj['id_team']) },
            'related': { 'href': _create_api_path('category', team.id_category) },
        }
        return obj

class Teams(TeamBase):
    def GET(self, slash=False):
        if slash:
            raise web.seeother('/teams')

        params = web.input(_unicode=True)
        result = []

        db = swissturnier.db.DB()
        with db.session_scope() as session:
            query = []
            if 'category' in params and len(params['category']) > 0:
                query.append(swissturnier.db.Category.name == params['category'])
            teams = (session
                .query(swissturnier.db.Team)
                .join(swissturnier.db.Team.category)
                .filter(*query)
                .all())
            for team in teams:
                result.append(self.get_team_dict(team))

        web.header('Content-Type', 'application/json')
        return api_json_encoder.encode({
            'count': len(result),
            'items': result,
            '_links': {
                'self': { 'href': _create_api_path('teams') },
            }
        })

class Team(TeamBase):
    def GET(self, id_team):
        db = swissturnier.db.DB()
        team = None
        with db.session_scope() as session:
            team = session.query(swissturnier.db.Team).get(int(id_team))
            if team is None:
                raise web.notfound(message='Team does not exist')
            obj = self.get_team_dict(team)

        web.header('Content-Type', 'application/json')
        return api_json_encoder.encode(obj)

class CurrentPlayRound(object):
    def GET(self):
        db = swissturnier.db.DB()
        current_round = None
        with db.session_scope() as session:
            current_round = swissturnier.db.query_current_round(session)
        return {
            'round': current_round,
        }
    
class PlayRoundBase(TeamBase):
    PLAYROUND_ATTRIBUTES = [
        'id_playround',
        'round_number',
        'id_team_a',
        'id_team_b',
        'points_a',
        'points_b',
        'start_time',
    ]

    def get_play_dict(self, playround):
        obj = {}
        for name in self.PLAYROUND_ATTRIBUTES:
            obj[name] = getattr(playround, name)
        obj['_embedded'] = {
            'team_a': self.get_team_dict(playround.team_a),
            'team_b': None if playround.team_b is None else self.get_team_dict(playround.team_b),
        }
        obj['_links'] = {
            'self': { 'href': _create_api_path('play', playround.id_playround) },
        }
        return obj
        
class PlayRounds(PlayRoundBase):

    def GET(self, round_number):
        params = web.input(_unicode=True)
        db = swissturnier.db.DB()
        results = []
        with db.session_scope() as session:
            filters = [swissturnier.db.PlayRound.round_number == int(round_number)]
            #if 'round' in params:
            #    filters.append(swissturnier.db.PlayRound.round_number == int(params['round']))

            playrounds = session.query(swissturnier.db.PlayRound).filter(*filters).order_by('id_playround').all()
            results = [self.get_play_dict(playround) for playround in playrounds]

        web.header('Content-Type', 'application/json')
        return api_json_encoder.encode({
            'count': len(results),
            'plays': results,
        })


class Play(PlayRoundBase):
    def GET(self, id_play):
        db = swissturnier.db.DB()
        obj = {}
        with db.session_scope() as session:
            play = session.query(swissturnier.db.PlayRound).get(int(id_play))
            obj = self.get_play_dict(play)
        web.header('Content-Type', 'application/json')
        return api_json_encoder.encode(obj)

    def PUT(self, id_play):
        data = json.loads(web.data())

        db = swissturnier.db.DB()
        with db.session_scope() as session:
            play = session.query(swissturnier.db.PlayRound).get(int(id_play))
            play.points_a = data.get('points_a')
            play.points_b = data.get('points_b')
            obj = self.get_play_dict(play)

        web.header('Content-Type', 'application/json')
        return api_json_encoder.encode(obj)


def get_application():
    return web.application(urls, globals())

if __name__ == '__main__':
    app = get_application()
    app.run()
