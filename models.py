 # __author__ = 'Piotr Dyba'

from flask_login import UserMixin

from sqlalchemy import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import String
from sqlalchemy.types import Boolean
from sqlalchemy.types import PickleType
from sqlalchemy.types import Date

from datetime import datetime

from main import db


class User(db.Model, UserMixin):
    """
    User model for reviewers.
    """
    __tablename__ = 'user'
    id = Column(Integer, autoincrement=True, primary_key=True)
    active = Column(Boolean, default=True)
    username = Column(String(20), unique=True)
    email = Column(String(200), unique=True)
    password = Column(String(200), default='')
    job=Column(String(20),default='')
    organizer = Column(Boolean, default=False)
    admin = Column(Boolean, default=False)
    birthdate = Column(String(20), default='')
    about = Column(db.Text(), default='')
    why = Column(db.Text(), default='')
    a=Column(Boolean, default=False)

    def is_active(self):
        """
        Returns if user is active.
        """
        return self.active

    def is_admin(self):
        """
        Returns if user is admin.
        """
        return self.admin

class Message(db.Model):
    """
    Message model
    """
    __tablename__ = 'message'
    id = Column(Integer,autoincrement=True, primary_key=True)
    title = Column(String(200))
    adresser = Column(String(20), default='')
    author = Column(String(20), default='')
    created = Column(db.DateTime(), nullable=False)
    content = Column(db.Text())
    new = Column(Boolean, default=True)


class Team(db.Model):
    """
    Team model
    """
    __tablename__ = 'team'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(20), unique=True)
    master_email = Column(String(200))
    master = Column(String(200))
    contributors = Column(PickleType())

class Jam(db.Model):
    """

    Jam model
    """
    __tablename__ = 'jam'
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String(20), unique=True)
    theme = Column(String(100))
    description = Column(db.Text())
    master_email = Column(String(200))
    master = Column(String(200))
    teams = Column(PickleType())
    active = Column(Boolean, default=True)


class Game(db.Model):
    """
    Game model
    """
    __tablename__ = 'game'
    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String(50), unique=True)
    team = Column(String(20), nullable=False)
    description = Column(String(200))
    jam = Column(String(20))
    path = Column(String(100))

