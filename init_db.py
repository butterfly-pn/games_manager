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

    user = models.User()
    user.username = "wikwoj"
    user.password = sha256_crypt.encrypt("wikwoj")
    user.email = 'wikwoj@xd.com'
    user.job= "pierwszy user"
    user.admin = False
    user.poweruser = True
    user.organizer = True
    user.birthdate = "01.01.1889"
    user.about = "Jestem dobrym szefem"
    user.why = "Chcę zwyciężyć każdy jam"
    db.session.add(user)
    db.session.commit()

    team = models.Team()
    team.name = "BestTeam"
    team.master = "piotr"
    team.master_email = 'piotr@dyba.com.pl'
    team.contributors = ['adam', 'innygosc', 'jakiskoles']
    db.session.add(team)
    db.session.commit()

    team = models.Team()
    team.name = "DrużynaWygrywów"
    team.master = "wikwoj"
    team.master_email = 'wikwo@xd.coml'
    team.contributors = ['wikwoj', 'bedegralwgre', 'jestemhardkorem']
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
    jam.theme="destruction"
    jam.description="Jam o rozwalaniu"
    jam.master_email = 'piotr@dyba.com.pl'
    jam.teams=['BestTeam']
    db.session.add(jam)
    db.session.commit()

    jam = models.Jam()
    jam.title = "Jam testowy2"
    jam.master = "piotr"
    jam.theme="destruction"
    jam.description="Jam o rozwalaniu"
    jam.master_email = 'piotr@dyba.com.pl'
    jam.teams = ['BestTeam', "DrużynaWygrywów"]
    db.session.add(jam)
    db.session.commit()

    jam = models.Jam()
    jam.title = "Szybki jam o dziwnych grach"
    jam.master = "wikwoj"
    jam.theme="Stranger things"
    jam.description="Jam o dziwnych i zwariowanych grach"
    jam.master_email = 'wikwoj@xd.com'
    jam.teams = ['DrozynaWygrywów']
    db.session.add(jam)
    db.session.commit()

    jam = models.Jam()
    jam.title = "Ten jam nie istnieje"
    jam.master = "wikwoj"
    jam.theme="matrix"
    jam.description="Jam o rniebyciu"
    jam.master_email = 'wikwoj@xd.com'
    jam.teams = ['DrozynaWygrywów']
    db.session.add(jam)
    db.session.commit()


    jam = models.Jam()
    jam.title = "Global game jam"
    jam.master = "wikwoj"
    jam.theme="Wszystkie gry"
    jam.description="Jam, w ktorym tolerowane sa wszystkie gatunki gier"
    jam.master_email = 'wikwoj@xd.com'
    jam.teams = ['DrozynaWygrywów']
    db.session.add(jam)
    db.session.commit()

    game = models.Game()
    game.title = "Demolition n' Destruction"
    game.team = "BestTeam"
    game.description = 'gra o rozwalaniu i zniszczeniu'
    game.jam = 'Szybki jam o dziwnych grach'
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
    game.jam = 'Global game jam'
    game.path = "Jabba The Hutt - Fat worm story.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Lightsaber tactics"
    game.team = "DrozynaWygrywów"
    game.description = 'Platformowa gra 2D, w której poruszasz się zbuntowanym rycerzem Jedi i zabijasz młodych adeptów'
    game.jam = 'JaTen jam nie istnieje'
    game.path = "Lightsaber tactics.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Military trucks"
    game.team = "DrozynaWygrywów"
    game.description = 'Prosta gra wyścigowa z pojazdami wojskowymi'
    game.jam = 'Jam testowy'
    game.path = "Military trucks.tar.xz"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Quit now"
    game.team = "BestTeam"
    game.description = 'Ciężka gra platformowa'
    game.jam = 'Jam testowy2'
    game.path = "Quit now.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Satelite destroyer"
    game.team = "DrozynaWygrywów"
    game.description = 'Jako operator działa niszcz zbliżające się satelity wroga'
    game.jam = 'Ten jam nie istnieje'
    game.path = "Satelite destroyer.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Shoot fast! Don't die!"
    game.team = "Dróżyna wygrywów"
    game.description = 'Multiplayer FPS typu arena'
    game.jam = 'Szybki jam o dziwnych grach'
    game.path = "Shoot fast! Don't die!."
    db.session.add(game)
    db.session.commit()

if __name__ == '__main__':
    db_start()