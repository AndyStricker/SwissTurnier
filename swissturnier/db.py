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
from sqlalchemy import Column, String, Integer, Float, ForeignKey
import sqlalchemy.orm
import sqlalchemy.ext.declarative
 
from contextlib import contextmanager
import urllib.parse
import json
import sys
import errno

Base = sqlalchemy.ext.declarative.declarative_base()
 
class DB(object):
    """ Encapsulate the ORM logic and provides sessions and transactions """

    def __init__(self, config_file='config.json'):
        self._config = {
            'database': 'swissturnier',
            'schema': 'postgres',
            'user': 'stuser',
            'password': None,
            'host': 'localhost',
            'port': 5432,
        }
        self._engine = None
        self._connection = None
        self._sessionmaker = None
        self._init_config(config_file)

    @property
    def config(self):
        """ Loaded configuration """
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def engine(self):
        """
        SQL Alchemy specific engine instance with the connection parameters
        to the DB.
        """
        if not self._engine:
            self._engine = sqlalchemy.create_engine(self._buildurl())
        return self._engine

    @property
    def connection(self):
        """ Return a connection to the DB. But better use a session instead """
        if not self._connection:
            self._connection = self.engine.connect()
        return self._connection

    @property
    def sessionmaker(self):
        """ SQL Alchemy specific session maker """
        if not self._sessionmaker:
            self._sessionmaker = sqlalchemy.orm.sessionmaker()
            self._sessionmaker.configure(bind=self.engine, autocommit=False)
        return sqlalchemy.orm.scoped_session(self._sessionmaker)

    def create_session(self):
        return self.sessionmaker()

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.create_session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def _init_config(self, config_file):
        try:
            with open(config_file, 'r') as f:
                fcfg = json.load(f)
                self._config.update(fcfg)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise

    def _buildurl(self):
        cfg = self.config.copy()
        cfg['credentials'] = cfg['user']
        if cfg['password']:
            cfg['credentials'] += ':' + urllib.parse.quote_plus(cfg['password'])
        return "{schema}://{credentials}@{host}:{port}/{database}".format(**cfg)

    def close(self):
        if self._connection:
            self._connection.close()
            self._connection = None

    def createdb(self):
        """ FIXME Never tried this method """
        Base.metadata.create_all(self.engine)

class DBError(Exception): pass


class Category(Base):
    """ A team category """
    __tablename__ = 'category'
    id_category = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)


class Team(Base):
    """ A team taking part on the turnier, with its category """
    __tablename__ = 'team'
    id_team = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    id_category = Column(ForeignKey('category.id_category'), nullable=False)
    category = sqlalchemy.orm.relationship(Category)


class PlayRound(Base):
    """ For each team encounter store the round and the teams """
    __tablename__ = 'playround'
    id_playround = Column(Integer, primary_key=True)
    round_number = Column(Integer, nullable=False)
    id_team_a = Column(ForeignKey('team.id_team'), nullable=False)
    id_team_b = Column(ForeignKey('team.id_team'))
    points_a = Column(Integer)
    points_b = Column(Integer)
    team_a = sqlalchemy.orm.relationship(Team, foreign_keys=id_team_a)
    team_b = sqlalchemy.orm.relationship(Team, foreign_keys=id_team_b)


class Rankings(Base):
    """ The ranking table based on all rounds played yet """
    __tablename__ = 'rankings'
    id_rank = Column(Integer, primary_key=True)
    id_team = Column(Integer, ForeignKey('team.id_team'))
    rank = Column(Integer)
    wins = Column(Float)
    points = Column(Integer)
    team = sqlalchemy.orm.relationship(
        Team,
        backref=sqlalchemy.orm.backref('teams', uselist=True, cascade='delete,all'))

