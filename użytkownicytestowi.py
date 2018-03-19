from sqlalchemy import create_engine
from main import db
import models
from passlib.hash import sha256_crypt

from datetime import datetime

from datetime import datetime
i="0"
user = models.User()
user.username = i
user.password = sha256_crypt.encrypt(i)
user.email = i
user.admin = True
user.poweruser = True
user.organizer = True
user.job = i
user.birthdate = "01.01.1999"
user.about = "Jestem użytkownikiem testowym"
user.why = "blablabla"
db.session.add(user)
db.session.commit()

for i in range(1,10):
    i=str(i)
    user = models.User()
    user.username = i
    user.password = sha256_crypt.encrypt(i)
    user.email = i
    user.job = i
    user.birthdate = "01.01.1999"
    user.about = "Jestem użytkownikiem testowym"
    user.why = "blablabla"
    db.session.add(user)
    db.session.commit()