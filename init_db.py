__author__ = 'Piotr Dyba'

from sqlalchemy import create_engine
from main import db
import models
from passlib.hash import sha256_crypt


def db_start():
    engine = create_engine('sqlite:///tmp/test.db', convert_unicode=True)
    db.create_all()
    db.session.commit()

    user = models.User()
    user.username = "piotr"
    user.password = sha256_crypt.encrypt("pppp1234")
    user.email = 'piotr@dyba.com.pl'
    user.job= "szef projektu"
    user.admin = True
    user.poweruser = True
    db.session.add(user)
    db.session.commit()

    team = models.Team()
    team.name = "BestTeam"
    team.master = "piotr"
    team.master_email = 'piotr@dyba.com.pl'
    team.contributors = ['adam', 'twojamama', 'jakiskoles']
    db.session.add(team)
    db.session.commit()


if __name__ == '__main__':
    db_start()
