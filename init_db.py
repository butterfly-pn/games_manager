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
    user.email = 'piotr@pn.com.pl'
    user.job = "szef projektu"
    user.admin = True
    user.poweruser = True
    user.organizer = True
    user.birthdate = "01.01.1999"
    user.about = "Jestem dobrym adminem"
    user.why = "Chcę organizować gamejam, poniewż uważam, że jest to jest to idealna forma rozwoju dla młodych ludzi."
    db.session.add(user)
    db.session.commit()

    user = models.User()
    user.username = "patryk"
    user.password = sha256_crypt.encrypt("pppp1234")
    user.email = 'patryk@pn.com.pl'
    user.job = "szef projektu"
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
    user.job = "pierwszy user"
    user.admin = False
    user.poweruser = True
    user.organizer = True
    user.birthdate = "01.01.1889"
    user.about = "Jestem dobrym szefem"
    user.why = "Chcę zwyciężyć każdy jam"
    db.session.add(user)
    db.session.commit()

    user = models.User()
    user.username = "marek"
    user.password = sha256_crypt.encrypt("marek")
    user.email = 'marek@mc.com'
    user.job = "programista"
    user.admin = False
    user.poweruser = True
    user.organizer = False
    user.birthdate = "01.01.1889"
    db.session.add(user)
    db.session.commit()

    user = models.User()
    user.username = "stefan"
    user.password = sha256_crypt.encrypt("stefan")
    user.email = 'stefan@onet.com'
    user.job = "dzwiękowiec"
    user.admin = False
    user.poweruser = True
    user.birthdate = "01.01.1889"
    db.session.add(user)
    db.session.commit()

    team = models.Team()
    team.name = "BestTeam"
    team.master = "patryk"
    team.master_email = 'patyk@pn.com.pl'
    team.contributors = ['adam', 'innygosc', 'jakiskoles']
    team.gameinjams = ['Jam testowy', 'Pierwszy jam', 'Ten jam nie istnieje']
    db.session.add(team)
    db.session.commit()

    team = models.Team()
    team.name = "DrużynaWygrywów"
    team.master = "wikwoj"
    team.master_email = 'wikwo@xd.coml'
    team.contributors = ['wikwoj', 'bedegralwgre', 'jestemhardkorem']
    team.gameinjams = ['Jam testowy', 'Szybki jam o dziwnych grach', 'Ten jam nie istnieje', 'Global game jam']
    db.session.add(team)
    db.session.commit()

    team = models.Team()
    team.name = "MonsterCouch"
    team.master = "marek"
    team.master_email = 'Marek@mc.coml'
    team.contributors = ['Krzyś', 'artur', 'Helena']
    team.gameinjams = ['Pierwszy jam', 'Szybki jam o dziwnych grach', 'Ten jam nie istnieje', 'Global game jam']
    db.session.add(team)
    db.session.commit()

    team = models.Team()
    team.name = "LameTeam"
    team.master = "stefan"
    team.master_email = 'stefan@onet.com'
    team.contributors = ['Chyzio', 'Zyzio', 'Dyzio']
    team.gameinjams = ['Pierwszy jam', 'Szybki jam o dziwnych grach', 'Global game jam']
    db.session.add(team)
    db.session.commit()

    message = models.Message()
    message.title = 'testowa wiadomość'
    message.adresser = 'patryk'
    message.author = 'wikwoj'
    message.content = 'No hej'
    message.created = datetime.now()
    db.session.add(message)
    db.session.commit()

    jam = models.Jam()
    jam.title = "Jam testowy"
    jam.master = "patryk"
    jam.theme = "destruction"
    jam.description = "Jam o rozwalaniu"
    jam.master_email = 'patryk@pn.com.pl'
    jam.teams = ['BestTeam', "DrużynaWygrywów"]
    jam.active = False
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
    game.title = "Diablo Origins"
    game.team = "DrużynaWygrywów"
    game.description = 'gra o niszczniu potworów'
    game.jam = 'Jam testowy'
    game.path = "Diablo Origins.zip"
    db.session.add(game)
    db.session.commit()

    jam = models.Jam()
    jam.title = "Pierwszy jam"
    jam.master = "patryk"
    jam.theme = "destruction"
    jam.description = "Jam o rozwalaniu"
    jam.master_email = 'patryk@pn.com.pl'
    jam.teams = ['BestTeam', "MonsterCouch", 'LameTeam']
    db.session.add(jam)
    db.session.commit()

    game = models.Game()
    game.title = "Doom 0"
    game.team = "BestTeam"
    game.description = 'Prequel Doom'
    game.jam = 'Pierwszy jam'
    game.path = "Doom 0.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Jabba The Hutt - Fat worm story"
    game.team = "MonsterCouch"
    game.description = 'Przemierzaj pustynię Tatooine pod postacią grubego robaka i zjadaj szturmowców'
    game.jam = 'Pierwszy jam'
    game.path = "Jabba The Hutt - Fat worm story.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Devil ain't cry"
    game.team = "LameTeam"
    game.description = 'Doprowadź diabła do płaczu'
    game.jam = 'Pierwszy jam'
    game.path = "devil ain't cry.zip"
    db.session.add(game)
    db.session.commit()

    jam = models.Jam()
    jam.title = "Szybki jam o dziwnych grach"
    jam.master = "wikwoj"
    jam.theme = "Stranger things"
    jam.description = "Jam o dziwnych i zwariowanych grach"
    jam.master_email = 'wikwoj@xd.com'
    jam.teams = ['DrużynaWygrywów', 'MonsterCouch', 'LameTeam']
    db.session.add(jam)
    db.session.commit()

    game = models.Game()
    game.title = "Lightsaber tactics"
    game.team = "DrużynaWygrywów"
    game.description = 'Platformowa gra 2D, w której poruszasz się zbuntowanym rycerzem Jedi i zabijasz młodych adeptów'
    game.jam = 'Szybki jam o dziwnych grach'
    game.path = "Lightsaber tactics.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Quit now"
    game.team = "MonsterCouch"
    game.description = 'Ciężka gra platformowa'
    game.jam = 'Szybki jam o dziwnych grach'
    game.path = "Quit now.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Worms arena"
    game.team = "LameTeam"
    game.description = 'Bijesz się na areni będąc robakiem'
    game.jam = 'Szybki jam o dziwnych grach'
    game.path = "worms arena.zip"
    db.session.add(game)
    db.session.commit()

    jam = models.Jam()
    jam.title = "Ten jam nie istnieje"
    jam.master = "patryk"
    jam.theme = "matrix"
    jam.description = "Jam o rniebyciu"
    jam.master_email = 'patryk@pn.com'
    jam.teams = ['DrużynaWygrywów', 'BestTeam', 'MonsterCouch']
    jam.active = False
    db.session.add(jam)
    db.session.commit()

    game = models.Game()
    game.title = "Satelite destroyer"
    game.team = "BestTeam"
    game.description = 'Jako operator działa niszcz zbliżające się satelity wroga'
    game.jam = 'Ten jam nie istnieje'
    game.path = "Satelite destroyer.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Wolfenstein: the old order"
    game.team = "DrużynaWygrywów"
    game.description = 'Gra, w której musisz zabić Wiliama Josepha Blazkowicza'
    game.jam = 'Ten jam nie istnieje'
    game.path = "Wolfenstein the old order!.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Path of Neo"
    game.team = "MonsterCouch"
    game.description = 'Symulator Wiary'
    game.jam = 'Ten jam nie istnieje'
    game.path = "Path of neo.zip"
    db.session.add(game)
    db.session.commit()

    jam = models.Jam()
    jam.title = "Global game jam"
    jam.master = "wikwoj"
    jam.theme = "Wszystkie gry"
    jam.description = "Jam, w ktorym tolerowane sa wszystkie gatunki gier"
    jam.master_email = 'wikwoj@xd.com'
    jam.teams = ['DrużynaWygrywów', "MonsterCouch", 'LameTeam']
    jam.active = False
    db.session.add(jam)
    db.session.commit()

    game = models.Game()
    game.title = "Military trucks"
    game.team = "MonsterCouch"
    game.description = 'Prosta gra wyścigowa z pojazdami wojskowymi'
    game.jam = 'Global game jam'
    game.path = "Military trucks.tar.xz"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Battle of tatooine"
    game.team = "DrużynaWygrywów"
    game.description = 'Jako operator działa niszcz zbliżające się statki wroga'
    game.jam = 'Global game jam'
    game.path = "Battle of tatooine.zip"
    db.session.add(game)
    db.session.commit()

    game = models.Game()
    game.title = "Shoot fast! Don't die!"
    game.team = "LameTeam"
    game.description = 'Multiplayer FPS typu arena'
    game.jam = 'Global game jam'
    game.path = "Shoot fast! Don't die!.zip"
    db.session.add(game)
    db.session.commit()


if __name__ == '__main__':
    db_start()