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
import swissturnier.db
import swissturnier.ranking
import swissturnier.report

from web.contrib.template import render_cheetah
import Cheetah.Template


PREFIX = '/v1'
urls = (
    '/', 'Index',
    PREFIX + '/ranking(/)?', 'APIv1Ranking',
    PREFIX + '/playtable(/)?', 'APIv1PlayTable',
    PREFIX + '/categories', 'APIv1Categories',
    PREFIX + '/category/(\d+)', 'APIv1Category',
#    PREFIX + '/teams(/)?', 'Teams',
#    PREFIX + '/team(/)?', 'Teams',
#    PREFIX + '/team/(\d+)', 'Team',
)

def _create_api_path(resource, rid):
    return '{0}/{1}/{2}'.format(PREFIX, resource, rid)


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
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

            render = render_cheetah('reports/api')
            return render.index(title='Teams', statistics=stats)

class APIv1Ranking:
    def GET(self, slash):
        if slash:
            raise web.seeother('/ranking')

        #turnier = swissturnier.ranking.Turnier(db)
        #ranking.rank()
        db = swissturnier.db.DB()
        report = swissturnier.report.HTMLRankingTableReport(db)
        return report.create()

class APIv1PlayTable:
    def GET(self, slash):
        if slash:
            raise web.seeother('/playtable')

        db = swissturnier.db.DB()
        report = swissturnier.report.HTMLPlayTable(db)
        return report.create()

class APIv1CategoryBase(object):
    CATEGORY_ATTRIBUTES = ['id_category', 'name']
    def get_category_dict(self, category): 
        obj = {}
        for name in self.CATEGORY_ATTRIBUTES:
            obj[name] = getattr(category, name)
        obj['link'] = {
            'rel': 'self',
            'href': _create_api_path('category', obj['id_category']),
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
            'result': result,
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

    def get_athlete_dict(self, team):
        obj = {}
        for name in self.TEAM_ATTRIBUTES:
            obj[name] = getattr(team, name)
        obj['category'] = team.category.name
        obj['link'] = {
            'rel': 'self',
            'href': _create_api_path('team', obj['id_team']),
        }
        obj['category_ref'] = {
            'rel': 'related',
            'href': _create_api_path('category', obj['category']),
        }
        return obj

#     def update_from_dict(self, team, data):
#         for name in self.TEAM_ATTRIBUTES:
#             field_type = type(getattr(team, name))
#             v = data.get(name)
#             if field_type is decimal.Decimal or type(v) is float:
#                 setattr(team, name, decimal.Decimal(v) if not v is None else None)
#             else:
#                 setattr(team, name, v)

# class Athletes(AthleteBase):
#     def GET(self, slash=False):
#         if slash:
#             raise web.seeother('/athletes')
# 
#         params = web.input(_unicode=True)
# 
#         db = athrank.db.DB()
#         query = []
#         if params.has_key('firstname') and len(params['firstname']) > 0:
#             query.append(athrank.db.Athlete.firstname == params['firstname'])
#         if params.has_key('lastname') and len(params['lastname']) > 0:
#             query.append(athrank.db.Athlete.lastname == params['lastname'])
#         if params.has_key('category') and len(params['category']) > 0:
#             query.append(athrank.db.Athlete.category == params['category'])
#         if params.has_key('sex') and len(params['sex']) > 0:
#             query.append(athrank.db.Athlete.sex == params['sex'])
#         if params.has_key('number') and len(params['number']) > 0:
#             query.append(athrank.db.Athlete.number == int(params['number']))
#         if params.has_key('section') and len(params['section']) > 0:
#             query.append(athrank.db.Athlete.r_section == athrank.db.Section.id_section)
#             query.append(athrank.db.Section.name == params['section'])
#         if params.has_key('name') and len(params['name']) > 0:
#             name_query = params['name'].replace('%', '%%').replace('*', '%').replace('_', '__').replace('?', '_').strip()
#             query.append(athrank.db.Athlete.firstname.like(name_query) |
#                          athrank.db.Athlete.lastname.like(name_query))
#         athletes = db.store.find(athrank.db.Athlete, *tuple(query))
#         athletes.order_by(athrank.db.Athlete.number)
#         result = []
#         for athlete in athletes:
#             result.append(self.get_athlete_dict(athlete))
# 
#         web.header('Content-Type', 'application/json')
#         return api_json_encoder.encode({
#             'count': len(result),
#             'result': result,
#         })
# 
#     def POST(self, slash=False):
#         if slash:
#             raise web.seeother('/athletes')
# 
#     def POST(self):
#         personal_data = web.input(
#             'firstname', 'lastname', 'section', 'year_of_birth', 'sex',
#             _unicode=True
#         )
# 
#         db = athrank.db.DB()
#         section = db.store.find(athrank.db.Section, name=personal_data.section)
#         if section.is_empty():
#             raise web.badrequest(
#                 message='Section "{0}" not found'.format(personal_data.section)
#             )
#         section = section.one()
# 
#         year_of_birth = int(personal_data.year_of_birth)
#         agecategory = db.store.find(
#             athrank.db.AgeCategory,
#             age_cohort=year_of_birth,
#             sex=personal_data.sex
#         )
#         if agecategory.is_empty():
#             raise web.badrequest(
#                 message='Category for year "{0}" and sex "{1}" not found'.format(
#                     personal_data.year_of_birth,
#                     personal_data.sex
#                 )
#             )
#         category = agecategory.one().category
# 
#         athlete = athrank.db.Athlete(
#             firstname=personal_data.firstname,
#             lastname=personal_data.lastname,
#             year_of_birth=year_of_birth,
#             sex=personal_data.sex,
#             section=section.id_section,
#             category=category
#         )
# 
#         db.store.add(athlete)
#         db.store.commit()
# 
#         web.ctx.status = '201 Created'
#         web.header('Location', _create_api_path('athlete', athlete.id_athlete))
#         web.header('Content-Type', 'application/json')
#         obj = self.get_athlete_dict(athlete)
#         return api_json_encoder.encode(obj)
# 
# class Athlete(AthleteBase):
#     def GET(self, id_athlete):
#         db = athrank.db.DB()
#         athlete = db.store.get(athrank.db.Athlete, int(id_athlete))
#         if athlete is None:
#             raise web.notfound(message='Athlete with this id not found')
#         obj = self.get_athlete_dict(athlete)
#         web.header('Content-Type', 'application/json')
#         return api_json_encoder.encode(obj)
# 
#     def PUT(self, id_athlete):
#         data = json.loads(web.data())
#         db = athrank.db.DB()
#         athlete = db.store.get(athrank.db.Athlete, int(id_athlete))
#         if athlete is None:
#             raise web.notfound(message='Athlete with this not found')
#         self.update_from_dict(athlete, data)
#         db.store.commit()
#         obj = self.get_athlete_dict(athlete)
#         return api_json_encoder.encode(obj)
# 
# class AthleteStartNumber(AthleteBase):
#     def GET(self, number):
#         db = athrank.db.DB()
#         athlete = db.store.find(athrank.db.Athlete, number=int(number))
#         if athlete.is_empty():
#             raise web.notfound(message='No Athlete with this start number found')
#         obj = self.get_athlete_dict(athlete.one())
#         web.header('Content-Type', 'application/json')
#         return api_json_encoder.encode(obj)
# 

def get_application():
    return web.application(urls, globals())

if __name__ == '__main__':
    app = get_application()
    app.run()
