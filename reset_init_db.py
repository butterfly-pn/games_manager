_author__ = 'Piotr Dyba'

from sqlalchemy import create_engine
from reset_main import db
import reset_models as models
from passlib.hash import sha256_crypt

from datetime import datetime


def db_start():
    engine = create_engine('sqlite:///tmp/reset.db', convert_unicode=True)
    db.create_all()
    db.session.commit()



if __name__ == '__main__':
    db_start()