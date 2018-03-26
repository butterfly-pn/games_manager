from reset_moving_files import new_database
new_database()

file = open('test.db', "w")
file.close()

from init_db import db_start
db_start()
from reset_models import User, Team, Message, Jam

from main import db as rdb
import models

users = User.query.order_by(User.id.asc()).all()
for u in users:
    user = models.User()
    user.username = u.username
    user.password = u.password
    user.email = u.email
    user.admin = u.admin
    user.organizer = u.organizer
    user.job = u.job
    user.birthdate = u.birthdate
    user.about = u.about
    user.why = u.why
    user.a = u.a
    rdb.session.add(user)
    rdb.session.commit()

teams = Team.query.order_by(Team.id.asc()).all()
for t in teams:
    team = models.Team()
    team.name = t.name
    team.master = t.master
    team.master_email = t.master_email
    team.contributors = t.contributors
    rdb.session.add(team)
    rdb.session.commit()

jams = Jam.query.order_by(Jam.id.asc()).all()
for j in jams:
    jam = models.Jam()
    jam.title = j.title
    jam.master = j.master
    jam.description = j.description
    jam.master_email = j.master_email
    jam.teams = j.teams
    rdb.session.add(jam)
    rdb.session.commit()

messages = Message.query.order_by(Message.id.asc()).all()
for m in messages:
    message = models.Message()
    message.title = m.title
    message.adresser = m.adresser
    message.author = m.author
    message.content = m.content
    message.created = m.created
    rdb.session.add(message)
    rdb.session.commit()

print("teraz przekopiuj ZMIANY z models do reset_models")