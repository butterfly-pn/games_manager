_author__ = 'Piotr Dyba'

from sqlalchemy import create_engine
from main import db
import models
from passlib.hash import sha256_crypt

from datetime import datetime


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
    user.organizer = True
    user.birthdate = "01.01.1999"
    user.about = "Jestem dobrym adminem"
    user.why = "Chcę organizować gamejam, poniewż uważam, że jest to jest to idealna forma rozwoju dla młodych ludzi."
    db.session.add(user)
    db.session.commit()

    team = models.Team()
    team.name = "BestTeam"
    team.master = "piotr"
    team.master_email = 'piotr@dyba.com.pl'
    team.contributors = ['adam', 'innygosc', 'jakiskoles']
    db.session.add(team)
    db.session.commit()

    message=models.Message()
    message.title = 'testowa wiadomość'
    message.adresser='piotr'
    message.author='wikwoj'
    message.content='No hej'
    message.created=datetime.now()
    db.session.add(message)
    db.session.commit()


    jam = models.Jam()
    jam.title = "Jam testowy"
    jam.master="piotr"
    jam.master_email = 'piotr@dyba.com.pl'
    jam.teams=['BestTeam']
    db.session.add(jam)
    db.session.commit()

    jam = models.Jam()
    jam.title = "Jam testowy2"
    jam.master = "piotr"
    jam.master_email = 'piotr@dyba.com.pl'
    jam.teams = ['BestTeam']
    db.session.add(jam)
    db.session.commit()

    game = models.Game()
    game.title = "Demolition n' Destruction"
    game.team = "BestTeam"
    game.description = 'gra o rozwalaniu i zniszczeniu'
    game.jam = 'Jam testowy'
    game.path = "Demolition n' Destruction.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Doom 0"
    game.team = "BestTeam"
    game.description = 'Prequel Doom'
    game.jam = 'Jam testowy'
    game.path = "Doom 0.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Jabba The Hutt - Fat worm story"
    game.team = "BestTeam"
    game.description = 'Przemierzaj pustynię Tatooine pod postacią grubego robaka i zjadaj szturmowców'
    game.jam = 'Jam testowy'
    game.path = "Jabba The Hutt - Fat worm story.zip"
    db.session.add(game)
    db.session.commit()

if __name__ == '__main__':
    db_start()