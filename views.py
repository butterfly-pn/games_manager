
import os
from main import app
from main import db
from models import User, Team, Message, Jam, Game
import gc
import re
from passlib.hash import sha256_crypt
from functools import wraps
from flask import  render_template, flash, request, redirect, url_for, session, send_from_directory
from wtforms import Form, validators, StringField, PasswordField, BooleanField, TextAreaField, SelectField, FileField
from werkzeug.utils import secure_filename
from datetime import datetime


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
target = os.path.join(APP_ROOT, 'games')
UPLOAD_FOLDER = target
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', 'tar', 'gz2'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



user = User()


def login_required(func):
    """Dekorator po którego dodaniu do ścieżki mają dostęp tylko zalogowani
    użytkownicy"""
    @wraps(func)
    def wrap(*args, **kwargs):
        if not 'logged_in' in session:
            flash("Musisz być zalogowany.", 'danger')
            return redirect('/')
        else:
            return func(*args, **kwargs)

    return wrap



@app.route("/cookies-accept")
def cookies_accept():
    session['accepted']=True
    if request.args.get('next'):
        return redirect(request.args.get('next'))
    return redirect('/')

@app.route("/cookies-about")
def cookies_about():
    session['accepted']=False
    if request.args.get('next'):
        return redirect(request.args.get('next'))
    return redirect('/')

@app.route("/background/<int:i>")
def bckground(i):
    session['background']="background"+str(i)+".jpg"
    print(session['background'])
    if request.args.get('next'):
        return redirect(request.args.get('next'))
    return redirect('/')


"""
Początek Rejstracji
"""


class RegistrationForm(Form):
    """Forma do rejestracji"""
    username = StringField('Nazwa użytkowania', [validators.Length(min=4, max=20)])
    email = StringField('Adres email', [validators.Length(min=6, max=50), validators.InputRequired('@')])
    password = PasswordField('Hasło',
                             [validators.DataRequired(),
                              validators.EqualTo('confirm',
                                                 message='Hasła muszą być jednakowe')])
    confirm = PasswordField('Powtórz hasło')

    job = SelectField('jaka jest twoja funkcja', choices=[('Programista', 'Programista'), ('Grafik', 'Grafik'), ('Dźwiękowiec', 'Dźwiękowiec')])

    accept_tos = BooleanField('Akceptuję Warunki użytkowania i Politykę prywatności'
                              '(zaktualizowana 17 stycznia 2018r.)', [validators.Required()])

@app.route('/register/', methods=["GET", "POST"])
def register():
    """Rejestruje użytkownika dopisując go do bazy danych automatycznie logując
    i ustawiając jego status na aktywny"""

    try:
        form = RegistrationForm(request.form)
        if request.method == "POST" and form.validate():
            username = form.username.data
            email = form.email.data
            job = form.job.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            used_username = User.query.filter_by(username=username).first()
            if used_username:
                flash('Ta nazwa użytkowania jest już zajęta, proszę wybierz inną.')
                return render_template('register.html', form=form)
            if "@" not in email:
                flash('Podałeś nieprawidłowy adres email')
                return render_template('register.html', form=form)
            user=User()
            user.email = email
            user.password = password
            user.username = username
            user.job = job
            user.organizer = False
            db.session.add(user)
            db.session.commit()
            flash("Dzięki za rejestrację!")
            gc.collect()
            session['logged_in'] = True
            session['username'] = username
            user_admin = User.query.filter_by(username=session['username']).first().admin
            return redirect(url_for('homepage'))
        return render_template('register.html', form=form)
    except Exception as error:
        flash(error)
        return redirect(url_for('homepage'))



"""
Koniec Rejstracji, Początek Logowania i Wylogowywania 
"""


@app.route('/login/', methods=["GET", "POST"])
def login():
    """Wysyła zapytanie do bazy danych o login użytkownika a następnie porównuje
    jego zhashowane hasło z hashem z bazy danych, jeżeli się zgadza ustawia status
    na aktywny"""
    try:
        if request.method == "POST":

            db_user = User.query.filter_by(username=request.form['username']).first()
            if db_user:
                db_password = db_user.password
                if sha256_crypt.verify(request.form['password'], db_password):
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    db_user.active = 1
                    db.session.commit()
                    flash("Jesteś zalogowany jako  " + session['username'])
                    return redirect(url_for('homepage'))

            db_user = User.query.filter_by(email=request.form['username']).first()
            if db_user:
                db_password = db_user.password
                if sha256_crypt.verify(request.form['password'], db_password):
                    session['logged_in'] = True
                    session['username'] = User.query.filter_by(email=request.form['username']).first().username
                    session['email'] = User.query.filter_by(email=request.form['username']).first().email
                    db_user.active = 1
                    db.session.commit()
                    flash("Jesteś zalogowany jako  " + session['username'])
                    return redirect(url_for('homepage'))

            flash("Niepoprawne dane")
            gc.collect()
        return redirect(url_for('homepage'))
    except Exception as e:
        flash(e)
        return redirect(url_for('homepage'))

@app.route("/logout/")
@login_required
def logout():
    """Wylogowuje ustawiając status na niaktywny"""
    try:
        bck=session['background']
        cookies=session['accepted']
        User.query.filter_by(username=session['username']).first().active = 0
        db.session.commit()
        session.clear()
        flash("Zostałeś poprawnie wylogowany.")
        gc.collect()
        session['accepted']=cookies
        session['background']=bck
        return redirect(url_for('homepage'))
    except Exception as e:
        flash(e)
        return redirect(url_for('homepage'))



"""
Koniec Logowania, Początek Podstawowych informacji o stronie
"""


@app.route("/")
def homepage():
    """Wyświetla stronę do testowania rejestracji i logowania"""
    user_member=False
    team_leader=False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
        team=Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader=True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    return render_template('main.html', organizer=organizer, admin=admin, member=user_member, team_leader=team_leader)


@app.route("/info/")
def info():
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
        team=Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader=True

    except KeyError:
        organizer = False
        admin = False
        user_member=False
    return render_template("info.html", organizer=organizer, admin=admin, member=user_member, team_leader=team_leader)


"""
Koniec podstawowych informacji o stronie, początek informacji o użytkowniku
"""


@app.route('/user/<username>/')
def user_info_id(username):
    """
    Tu będą wyświetlane gamejamy, drużyny, gry i dokłade dane dotyczące użytkownika
    """
    if User.query.filter_by(username=username).first():
        if username==session['username'] and session['username']=='piotr' or username!="piotr":
            user=User.query.filter_by(username=username).first()
            if user:

                user_member=False
                team_leader = False
                try:
                    organizer = User.query.filter_by(username=session['username']).first().organizer
                    team = Team.query.filter_by(master=session['username']).all()
                    if team:
                        team_leader = True
                    admin = User.query.filter_by(username=session['username']).first().admin
                    admin = User.query.filter_by(username=session['username']).first().admin
                    teams=Team.query.order_by(Team.id.asc()).all()
                    for t in teams:
                        if session['username'] in t.contributors:
                            user_member = True
                except KeyError:
                    organizer = False
                    admin = False
                    user_member=False
                user=User.query.filter_by(username=username).first()
                user_teams=Team.query.filter_by(master=username).all()
                teams = Team.query.order_by(Team.id.asc()).all()
                in_teams = []
                for team in teams:
                    if user.username in team.contributors:
                        in_teams.append(team)
                messages = Message.query.filter_by(adresser=username).order_by(Message.created.desc()).all()
                new_messages=0
                for message in messages:
                    if message.new:
                        new_messages += 1
                return render_template('user_info.html', job=User.query.filter_by(username=session['username']).first().job, user=user, teams=in_teams,teams2=user_teams, organizer=organizer, admin=admin, new_messages=new_messages, member=user_member, team_leader=team_leader)
            flash("Błąd, nie ma tego użytkownika", 'warning')
            return redirect("/")
        return redirect('/user/'+session['username'])
    flash("Nie ma tego użytkownika", 'warning')
    return redirect("/")

@app.route('/user/<username>/messages/')
@login_required
def user_messages(username):
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    if session['username']==username or User.query.filter_by(username=session['username']).first().admin:

        messages=Message.query.filter_by(adresser=username).order_by(Message.created.desc()).all()
        new_messages=Message.query.filter_by(adresser=username, new=True).order_by(Message.created.desc()).all()
        old_messages = Message.query.filter_by(adresser=username, new=False).order_by(Message.created.desc()).all()
        try:
            return render_template('user_messages.html', messages=messages, user=username, organizer=organizer, admin=admin, member=user_member, new_messages=new_messages, old_messages=old_messages, team_leader=team_leader)
        except:
            return redirect('/')

@app.route('/message/<id>')
@login_required
def message_wdw(id):
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    if session['username'] == Message.query.filter_by(id=id).first().adresser or User.query.filter_by(username=session['username']).first().admin:
        message=Message.query.filter_by(id=id).first()
        if message.new:
            message.new=False
            db.session.commit()
        return render_template("message_normal.html", message=message, user=Message.query.filter_by(id=id).first().adresser, organizer=organizer, admin=admin, member=user_member, team_leader=team_leader)
    return redirect("/")


@app.route('/message/create', methods=['GET','POST'])
@login_required
def message_create():

    if request.method=='GET':
        if Team.query.filter_by(master=session['username']).all():
            team_leader=True
        return render_template('user_messages.html', organizer=User.query.filter_by(username=session['username']).first().organizer, admin=User.query.filter_by(username=session['username']).first().admin, team_leader=team_leader)
    else:
        name=request.form['username']
        title=request.form['title']
        content=request.form['content']
        if not User.query.filter_by(username=name).first():
            flash("nie ma takiego użytkownika")
            return redirect('/user/' + session['username']+"/messages")

        new_message=Message()
        new_message.adresser=name
        new_message.title=title
        new_message.content=content
        new_message.author=session['username']
        new_message.created=datetime.now()
        db.session.add(new_message)
        db.session.commit()
        flash("Wiadomość została wysłana")
        return redirect('/user/' + session['username']+"/messages")

@app.route('/message/<id>/delete')
@login_required
def message_delete(id):
    message=Message.query.filter_by(adresser=session["username"], id=id).first()
    if message:
        db.session.delete(message)
        db.session.commit()
    flash("Wiadomość została usunięta")
    return redirect('/user/' + session['username']+"/messages")

"""
Koniec informacji o użytkowniku, początek informacji o organizatorach
"""


class OrganizerForm(Form):
    fullname = StringField('Imię i nazwisko', [validators.InputRequired(' ')])
    birthdate_day = StringField('Data urodzenia', [validators.Length(min=1)])
    birthdate_month = StringField('Data urodzenia', [validators.Length(min=2)])
    birthdate_year = StringField('Data urodzenia', [validators.Length(min=4)])
    about = TextAreaField('O sobie')
    why = TextAreaField('Dlaczego chcesz organizować gamejam?')

@app.route('/become-organizer/', methods=['GET', 'POST'])
@login_required
def become_organizer():
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    try:
        form = OrganizerForm(request.form)
        if request.method == "POST" and form.validate():
            fullname = form.fullname.data
            birthdate_day = form.birthdate_day.data
            birthdate_month = form.birthdate_month.data
            birthdate_year = form.birthdate_year.data
            birthdate=birthdate_day+"."+birthdate_month+"."+birthdate_year
            about = form.about.data
            why = form.why.data
            organizer = User.query.filter_by(username=session['username']).first()
            organizer.fullname = fullname
            organizer.birthdate = birthdate
            organizer.about = about
            organizer.why = why
            for admin in User.query.filter_by(admin=True).all():
                name = admin.username
                title = 'Nowe zgłoszenie na organizatora'
                content = 'Użytkownik '+str(session['username'])+' chce zostać organizatorem <br> Imię i nazwisko: '+str(fullname)+'<br> Data urodzenia: '+str(birthdate)+'<br> O mnie: '+str(about) +'<br> Dlaczego: '+str(why) +'<br><br> <a href=\'/make-organizer/'+session['username']+'\'>Kliknij tu</a> aby zatwierdzić jego zgłoszenie'
                new_message = Message()
                new_message.adresser = name
                new_message.title = title
                new_message.content = content
                new_message.author = session["username"]
                new_message.created = datetime.now()
                db.session.add(new_message)
            db.session.commit()
            flash("Przyjęto zgłoszenie!")
            gc.collect()
            return redirect(url_for('homepage'))
        return render_template('become-organizer.html', form=form, organizer=organizer, admin=admin, member=user_member, team_leader=team_leader)
    except Exception as error:
        flash(error)
        return redirect(url_for('homepage'))

@app.route('/make-organizer/<username>')
@login_required
def make_organizer(username):
    if User.query.filter_by(username=session['username']).first().admin:
        if User.query.filter_by(username=username).first():
            User.query.filter_by(username=username).first().organizer = True
            db.session.commit()
            flash("Użytkownik "+username+" jest organizatorem!")
            return redirect('/admin/user/' + str(User.query.filter_by(username=username).first().id))
        else:
            flash("Błąd: Użytkownik nie istnieje")
            return redirect('/admin/')
    else:
        flash("Błąd: Nie masz uprawnień")
        return redirect('/user/' + session['username'])

@app.route('/take-organizer/<username>')
@login_required
def take_organizer(username):
    if User.query.filter_by(username=session['username']).first().admin:
        if User.query.filter_by(username=username).first():
            User.query.filter_by(username=username).first().organizer = False
            db.session.commit()
            flash("Użytkownik "+username+" już nie jest organizatorem!")
            return redirect('/admin/user/' + str(User.query.filter_by(username=username).first().id))
        else:
            flash("Błąd: Użytkownik nie istnieje")
            return redirect('/admin/')
    else:
        flash("Błąd: Nie masz uprawnień")
        return redirect('/user/' + session['username'])


"""
Koniec informacji o organizatorach, początek usuwania użytkownika
"""


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    """NIE DZIAłA NA UŻYTKOWNIKA PIOTR"""
    """Funkcja usuwa użytkownika, po czym jeżeli zalogoway użytkownik to admin, zwraca listę użytkowników, w przeciwnym przypadku wraca na stronę główną"""
    if id == User.query.filter_by(username=session['username']).first().id or User.query.filter_by(
            username=session['username']).first().admin:
        user = User.query.filter_by(id=id).first()
        if user:
            messages=Message.query.filter_by(adresser=user.username).all()
            for message in messages:
                db.session.delete(message)
            db.session.commit()
            gc.collect()
            jams=Jam.query.filter_by(master=user.username).all()
            for jam in jams:
                if jam:
                    jam.active = False
                    db.session.commit()

            teams=Team.query.order_by(Team.id.asc()).all()
            if teams:
                for team in teams:
                    if user.username in team.contributors:
                        cont=team.contributors[:]
                        cont.remove(user.username)
                        team.contributrs=cont[:]
                        db.session.commit()
                        del(team.contributors[0])
                        db.session.commit()
                        flash("usunięto usera z drużyny")
                        db.session.commit()

            teams=Team.query.filter_by(master=user.username)
            if teams:
                for team in teams:
                        db.session.delete(team)
                        db.session.commit()

            if id == User.query.filter_by(username=session['username']).first().id:
                db.session.delete(user)
                db.session.commit()
                flash('Usunięto użytkownika')
                try:
                    session.clear()
                    gc.collect()
                    flash('Usunięto użytkownika')
                    return redirect(url_for('homepage'))
                except Exception as e:
                    flash(e)
                    flash('Usunięto użytkownika')
                    return redirect(url_for('homepage'))
            else:
                db.session.delete(user)
                db.session.commit()
                flash('Usunięto użytkownika')
                return redirect('/user_list')
    return redirect('/')


"""
Koniec usuwania użytkownika, początek obsługi drużyn
"""


@app.route('/teams')
def teams():
    """Wyświetla listę zarejstrowanych drużyn, z linkami do nich"""

    user_member = False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        admin = User.query.filter_by(username=session['username']).first().admin
        teams = Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
    except KeyError:
        organizer = False
        admin = False
        user_member = False
    teams = Team.query.order_by(Team.id.asc()).all()
    return render_template("teams.html", teams=teams, admin=admin, organizer=organizer, member=user_member, team_leader=team_leader)


@app.route("/team/<team_name>")
def team(team_name):
    """wyświetla informacje o drużynie"""
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True

    except KeyError:
        organizer = False
        admin = False
        user_member=False
    this_team = Team.query.filter_by(name=team_name).first()
    admin = User.query.filter_by(username=session['username']).first().admin
    if this_team:
        return render_template("team.html", team=this_team, organizer=organizer, admin=admin, member=user_member, team_leader=team_leader)
    return render_template('404.html'), 404


class NewTeamForm(Form):

    name = StringField('Nazwa zespołu', [validators.Length(min=4, max=20)])

@app.route('/create-team/', methods=["GET", "POST"])
@login_required
def create_team():
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    if not team_leader:
        try:
            form = NewTeamForm(request.form)
            if request.method == "POST" and form.validate():
                name = form.name.data
                used_name = Team.query.filter_by(name=name).first()
                if used_name:
                    flash('Ta nazwa użytkowania jest już zajęta, proszę wybierz inną.')
                    return render_template('create-team.html', form=form, organizer=organizer, admin=admin, member=user_member, team_leader=team_leader)
                new_team = Team()
                new_team.name = name
                new_team.master = session['username']
                new_team.master_email = User.query.filter_by(username=session['username']).first().email
                new_team.contributors = [session['username']]
                db.session.add(new_team)
                db.session.commit()
                flash("Zespół został stworzony!")
                gc.collect()
                return redirect(url_for('homepage'))
            return render_template('create-team.html', form=form, organizer=organizer, admin=admin, member=user_member, team_leader=team_leader)
        except Exception as error:
            flash(error)
            return redirect(url_for('homepage'))
    return redirect(url_for('homepage'))

@app.route('/delete-team/<team_name>')
@login_required
def delete_team(team_name):
    try:
       if User.query.filter_by(username=session['username']).first().admin or Team.query.filter_by(name=team_name).first().master == session['username']:
           this_team = Team.query.filter_by(name=team_name).first()
           messages=Message.query.filter_by(author=this_team.master, title="Zaproszenie do drużyny "+team_name).all()
           for message in messages:
               db.session.delete(message)
               db.session.commit()
           db.session.delete(this_team)
           db.session.commit()
           flash("Usunięto zespół!")
           return redirect(url_for('homepage'))
       else:
           flash("Nie masz uprawnień")
           return redirect(url_for('homepage'))
    except Exception as error:
        flash(error)
        return redirect(url_for('homepage'))


@app.route('/team/<team_name>/invite', methods=['GET','POST'])
@login_required
def invite_redirect(team_name):
    if request.method=='GET':
        return render_template('team.html', organizer=User.query.filter_by(username=session['username']).first().organizer, admin=User.query.filter_by(username=session['username']).first().admin, team_leader=team_leader)
    else:
        name=request.form['username']
        if not Message.query.filter_by(adresser=name, title="Zaproszenie do drużyny "+team_name).first():
            if User.query.filter_by(username=name).first():
                return redirect("/team/"+team_name+'/invite/'+name)
            flash("Nie ma takiego użytkownika")
            return redirect('/team/'+team_name)
        flash("Ten użytkownik został już zaproszony")
        return redirect('/team/' + team_name)

@app.route('/team/<team_name>/invite/<username>')
@login_required
def team_invite(team_name,username):
    teams1=Team.query.order_by(Team.id.asc()).all()
    for team1 in teams1:
        if username in team1.contributors:
            flash('Ten użytkownik jest już w jakiejś drużynie', 'warning')
            return redirect("/team/"+team_name)


    if User.query.filter_by(username=session['username']).first().admin or Team.query.filter_by(name=team_name).first().master==session['username']:
        message=Message.query.filter_by(author=Team.query.filter_by(name=team_name).first().master, adresser=username, title="Zaproszenie do drużyny "+team_name).first()
        if not message:
            new_message = Message()
            new_message.title ="Zaproszenie do drużyny "+team_name
            new_message.author =Team.query.filter_by(name=team_name).first().master
            new_message.adresser =username
            new_message.created=datetime.now()
            new_message.content = "Zostałeś zaproszony do drużyny "+team_name+". W tej drużynie znajdują się: "+str(Team.query.filter_by(name=team_name).first().contributors)
            db.session.add(new_message)
            db.session.commit()
            flash("użytkownik został zaproszony")
        else:
            flash("Użytkonik był już zaproszony. Poczekaj na jego odpowiedź")
        return redirect('/team/'+team_name)
    return redirect("/")


@app.route('/team/<team_name>/join/<username>')
@login_required
def team_join(team_name, username):
    teams1=Team.query.order_by(Team.id.asc()).all()
    for team1 in teams1:
        if username in team1.contributors:
            flash('Ten użytkownik jest już w jakiejś drużynie', 'warning')
            return redirect("/team/"+team_name)

    if User.query.filter_by(username=session['username']).first().admin or Message.query.filter_by(title="Zaproszenie do drużyny "+team_name, adresser=username).first().adresser==username:
        team=Team.query.filter_by(name=team_name).first()
        if team:
            if not username in Team.query.filter_by(name=team_name).first().contributors:
                if team.contributors:
                    cont=team.contributors[:]
                    cont.append(username)
                    team.contributors=cont[:]
                    db.session.commit()
                    flash('Pomyślnie dołączono do drużyny')
                else:
                    cont=team.contributors[:]
                    cont=[username]
                    team.contributors=cont[:]
                    db.session.commit()
                    flash('Pomyślnie dołączono do drużyny')
            return redirect('/team/'+team_name)
        flash("Błąd:  nie ma takiej drużyny")
    return redirect('/')


@app.route('/join-team/<team_name>')
@login_required
def join_team(team_name):
    username=session['username']
    team=Team.query.filter_by(name=team_name).first()
    teams1=Team.query.order_by(Team.id.asc()).all()
    for team1 in teams1:
        if username in team1.contributors:
            flash('Jesteś już w jakiejś drużynie', 'warning')
            return redirect("/team/"+team_name)
    message=Message.query.filter_by(author=username, adresser=team.master, title="Prośba o dołączenie do drużyny "+team_name).first()
    if not message:
        new_message = Message()
        new_message.title ="Prośba o dołączenie do drużyny "+team_name
        new_message.author =username
        new_message.adresser =Team.query.filter_by(name=team_name).first().master
        new_message.created=datetime.now()
        new_message.content = "Użytkownik "+username+"Chce dołączyć do twojej drużyny "+team_name+'<br><br>  <a href=\'/team/'+team_name+'/add/'+username+'\' style="color: #000000">Kliknij tu</a> aby zatwierdzić jego zgłoszenie'
        db.session.add(new_message)
        db.session.commit()
        flash("Wysłano prośbę o dołączenie")
    else:
        flash("Użytkonik był już zaproszony. Poczekaj na jego odpowiedź")
    return redirect('/team/'+team_name)

@app.route('/team/<team_name>/add/<username>')
@login_required
def add_team(team_name, username):
    team=Team.query.filter_by(name=team_name).first()
    teams1=Team.query.order_by(Team.id.asc()).all()
    for team1 in teams1:
        if username in team1.contributors:
            flash('Użytkownk jest już w jakiejś drużynie', 'warning')
            return redirect("/team/"+team_name)
    message=Message.query.filter_by(author=username, adresser=team.master, title="Prośba o dołączenie do drużyny "+team_name).first()
    if message:
        db.session.delete(message)
        if team.contributors:
            cont = team.contributors[:]
            cont.append(username)
            team.contributors = cont[:]
            db.session.commit()
            flash('Pomyślnie dołączono do drużyny')
        else:
            cont = team.contributors[:]
            cont = [username]
            team.contributors = cont[:]
            db.session.commit()
            flash('Pomyślnie dołączono do drużyny')
    else:
        return redirect("/")

@app.route("/team/<team_name>/give//1")
@login_required
def team_redirect(team_name):
    """obsługa wrednego błędu"""
    flash("nie ma takiego użytkownika", 'warning')
    return redirect('/team/'+team_name)

@app.route("/team/<team_name>/give_redirect",methods=["GET","POST"])
@login_required
def give_redirect(team_name):
    """zbiera informacje s formulaża"""
    if request.method=="GET":
        return render_template("team.html",team=Team.query.filter_by(name=team_name).first())
    name = request.form['give_name']
    if User.query.filter_by(username=name).first():
        return redirect('/team/'+team_name+'/give/'+name+'/1')
    flash('nie ma takiego użytkownika',"warning")
    return redirect('/team/'+team_name)

@app.route('/team/<team_name>/give/<username>/<int:i>')
@login_required
def team_give(team_name,username,i):
    """przekazuje drużynę
    'i' jest etapem przekazywania
    nnie chciałem tego pisaćw dwuch funkcjach

    """

    teams1=Team.query.order_by(Team.id.asc()).all()
    for team1 in teams1:
        if username in team1.contributors:
            flash('Ten użytkownik jest już w jakiejś drużynie', 'warning')
            return redirect("/team/"+team_name)

    if i==1:
        if User.query.filter_by(username=session['username']).first().admin and not Team.query.filter_by(name=team_name).first().master==session['username']:
            return redirect('/team/'+team_name+"/give/"+username+"/2")
        if Team.query.filter_by(name=team_name).first().master==session['username']:
            message=Message.query.filter_by(author=Team.query.filter_by(name=team_name).first().master, adresser=username, title="Prośba o przejęcie drużyny "+team_name).first()
            if not message:
                new_message = Message()
                new_message.title ="Prośba o przejęcie drużyny "+team_name
                new_message.author =Team.query.filter_by(name=team_name).first().master
                new_message.adresser =username
                new_message.created=datetime.now()
                new_message.content = "Zostałeś zaproszony do objcia prowadzenia w drużynie "+team_name+"<br> Dotychczasowym szefem tej drużyny był "+Team.query.filter_by(name=team_name).first().master+' <br><br> <a href=\'/team/'+team_name+'/give/'+username+'/2''\'>Kliknij tu</a> aby zatwierdzić jego zgłoszenie '
                db.session.add(new_message)
                db.session.commit()
                flash("użytkownik został zaproszony")
            else:
                flash("Użytkonik był już zaproszony. Poczekaj na jego gdpowiedź")
            return redirect('/team/'+team_name)
        flash("nie masz uprawnień")
        return redirect("/")


    if i==2:
        try:
            message=Message.query.filter_by(author=Team.query.filter_by(name=team_name).first().master, adresser=username, title="Prośba o przejęcie drużyny "+team_name).first()
        except Exception as e:
            flash(e)
            return redirect("/")

        if message:
            if message.adresser==session['username']:
                team=Team.query.filter_by(name=team_name).first()
                if not User.query.filter_by(username=session['username']).first().admin:
                    new_message = Message()
                    new_message.title = "Drużyna  " + team_name+" została przekazana"
                    new_message.author = username
                    new_message.adresser = Team.query.filter_by(name=team_name).first().master
                    new_message.created = datetime.now()
                    new_message.content = "Drużyna team została przez ciebie przekazana użytkownikowi user. <br> Jeżeli nie było to twoje działanie, możesz skontaktować się z naszą admiistracją."
                    db.session.add(new_message)
                    db.session.commit()


                user=User.query.filter_by(username=username).first()
                team.master=user.username
                team.master_email=user.email
                db.session.commit()

                team = Team.query.filter_by(name=team_name).first()
                if team:
                    if not user.username in Team.query.filter_by(name=team_name).first().contributors:
                        if team.contributors:
                            cont = team.contributors[:]
                            cont.append(user.username)
                            team.contributors = cont[:]
                            db.session.commit()
                            flash('Pomyślnie dołączono do drużyny')
                        else:
                            cont = team.contributors[:]
                            cont = [username]
                            team.contributors = cont[:]
                            db.session.commit()
                            flash('Pomyślnie dołączono do drużyny')


                return redirect("/team/"+team_name)
            return redirect("/")
        elif User.query.filter_by(username=session['username']).first().admin:
            team = Team.query.filter_by(name=team_name).first()
            team.master = username
            db.session.commit()
            return redirect("/team/" + team_name)
    return redirect("/")

@app.route('/team/<team_name>/delete/<username>')
@login_required
def team_delete(team_name, username):
    if User.query.filter_by(username=session['username']).first().admin or Team.query.filter_by(name=team_name).first().master == session['username']:
        for contributor in Team.query.filter_by(name=team_name).first().contributors:
            if contributor == username:
                contributors = Team.query.filter_by(name=team_name).first().contributors
                contributors.remove(contributor)
                Team.query.filter_by(name=team_name).first().contributors = contributors
                db.session.commit()
                invite_message = Message.query.filter_by(adresser=username, title = "Zaproszenie do drużyny "+team_name).first()
                if invite_message:
                    db.session.delete(invite_message)
                    db.session.commit()
                flash('Pomyślnie usunięto username z drużyny'.replace('username', username))
                return redirect('team/'+team_name)
        flash('Błąd: Nie ma takiego użytkownika')
        return redirect('team/'+team_name)
    else:
        flash("Błąd: Nie masz uprawnień", category='error')
        return redirect('team/'+team_name)


"""
Koniec obsługi drużyn, początek obsługi jamów
"""


class JamCreationForm(Form):
    jam_name =  StringField("nazwa GAME-JAMu", [validators.InputRequired(' ')])
    jam_theme = StringField("motyw przewodni jamu", [validators.InputRequired(' ')])
    jam_description = StringField("opis gamejamu", [validators.InputRequired(' ')])

@app.route('/create-jam/', methods=['GET', 'POST'])
@login_required
def jam_creation():
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    try:
        if admin or organizer:
            form = JamCreationForm(request.form)
            if form.validate():
                name = form.jam_name.data
                theme = form.jam_theme.data
                description=form.jam_description.data
                master = User.query.filter_by(username=session['username']).first()
                new_jam = Jam()
                new_jam.title=name
                new_jam.theme=theme
                new_jam.description = description
                new_jam.master=master.username
                new_jam.master_email=master.email


                new_jam.active=True
                db.session.add(new_jam)
                db.session.commit()
                flash("Jam stworzony!")
                gc.collect()
                return redirect(url_for('homepage'))
            flash("Operacja nie powiodła się")
            return redirect('/')
        flash('Nie masz uprawnień aby wchodzić na tą stronę')
        return redirect(url_for('homeage'))
    except Exception as error:
        flash(error)
        return redirect(url_for('homepage'))


@app.route('/jams')
def jams():
    """Wyświetla listę jamów, z linkami do nich"""
    teams=Team.query.order_by(Team.id).all()
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    except KeyError:
        organizer = False
        admin = False
        user_member=False

    time_now=str(datetime.now())
    day=time_now[9:12]
    hour=time_now[11:14]
    minute=time_now[15:18]
    jams = Jam.query.order_by(Jam.id.asc()).all()
    return render_template("jams.html", jams=jams, admin=admin, organizer=organizer, member=user_member, team_leader=team_leader)
    # return redirect('/')

@app.route("/jam/<jam_id>")
def jam(jam_id):
    """wyświetla informacje o jamie"""
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    this_jam = Jam.query.filter_by(id=jam_id).first()
    admin = User.query.filter_by(username=session['username']).first().admin
    team = Team.query.filter_by(master=session['username']).first()
    jam_master=Jam.query.filter_by(master=session['username'])
    game=Game.query.filter_by(jam=this_jam.title).all()
    teamsxd=[]
    for i in this_jam.teams:
        teamsxd.append(Team.query.filter_by(name=i).first())

    userteam=Team.query.filter_by(master=session['username']).first()
    if this_jam:
        return render_template("jam.html", jam=this_jam, organizer=organizer, admin=admin, member=user_member,teams=team, team_leader=team_leader, games=game, userteam=userteam, teamsxd=teamsxd)
    return render_template('404.html'), 404


@app.route('/jam/<jam_id>/invite/<team_name>')
@login_required
def jam_invite(jam_id,team_name):
    try:
        jam=Jam.query.filter_by(id=jam_id).first()
        if jam.master==session['username'] or User.query.filter_by(username=session['username']).first().admin:
            return redirect("/jam/jam_id/add/team".replace("jam_id", jam_id).replace("team", team_name))

        jam_master = Jam.query.filter_by(id=jam_id).first().master
        title = "Prośba o dołączenie drużyny do jamu gamejam".replace("gamejam", jam.title)
        message = Message.query.filter_by(adresser=jam_master, title=title, author="Drużyna " + team_name ).first()

        if not message:
            message = Message()
            message.title="Prośba o dołączenie drużyny do jamu gamejam".replace("gamejam",jam.title)
            message.adresser=jam.master
            message.author="Drużyna "+team_name
            message.content='Drużyna '+team_name+' chce brać udział w twoim jamie <br><br>  <a href=\'/jam/'+jam_id+'/add/'+team_name+'\' style="color: #000000">Kliknij tu</a> aby zatwierdzić jego zgłoszenie'
            message.created=datetime.now()
            db.session.add(message)
            db.session.commit()
            flash("Zgłoszenie wysłane")
            return redirect("/jam/"+jam_id)
        flash("Już wysłałeś zgłoszenie. Poczekaj na zatwierdzenie go przez organizatora")
        return redirect("/jam/" + jam_id)
    except Exception as e:
        flash(e)
        return redirect("/")


@app.route('/jam/<jam_id>/add/<team_name>')
@login_required
def jam_add(jam_id, team_name):

    admin = User.query.filter_by(username=session['username']).first().admin
    jam_master = Jam.query.filter_by(id=jam_id).first().master
    title = "Prośba o dołączenie drużyny team do twojego gamejamu".replace("team", team_name)
    message = Message.query.filter_by(adresser=jam_master,title=title)
    team = Team.query.filter_by(name=team_name).first()
    jams = Jam.query.order_by(Jam.id.asc()).all()
    i = 0
    for jam in jams:
        if team.name in jam.teams and jam.active:
            i += 1
    if i > 1:
        flash("ta drużyna jest już w dwóch innych jamach")
        return redirect("/jam/"+str(Jam.query.filter_by(id=jam_id).first().id))
    if admin or message and jam_master==session['username']:
        jam = Jam.query.filter_by(id=jam_id).first()
        if jam:
            if jam.teams:
                if not team_name in jam.teams:
                    jam = Jam.query.filter_by(id=jam_id).first()
                    teams=jam.teams[:]
                    teams.append(team_name)
                    jam.teams=teams[:]
                    db.session.commit()
                    flash('Pomyślnie dodamo drużyne do jamu')

            else:
                jam = Jam.query.filter_by(id=jam_id).first()
                jam.teams=[team_name]
                db.session.commit()
                db.session.commit()
                flash('Pomyślnie dodamo drużyne do jamu')

            return redirect('/jam/' + jam_id)
        return redirect("/")
    return redirect('/')


@app.route('/jam/<jam_id>/delete/<team_name>')
@login_required
def jam_delete(team_name, jam_id):
    if User.query.filter_by(username=session['username']).first().admin or Jam.query.filter_by(id=jam_id).first().master == session['username']:
        jam=Jam.query.filter_by(id=jam_id).first()
        if jam:
            if jam.teams:
                if team_name in jam.teams:
                    teams = jam.teams[:]
                    teams.remove(team_name)
                    jam.teams=teams[:]
                    db.session.commit()
                    invite_message = Message.query.filter_by(adresser=jam.master, author="Drużyna "+team_name).first()
                    if invite_message:
                        db.session.delete(invite_message)
                        db.session.commit()
                    flash('Pomyślnie usunięto team z jamu'.replace('team', team_name))
                    return redirect('jam/'+jam_id)
            flash('Błąd: W tym jamie nie ma drużyny team'.replace('team', team_name))
            return redirect('jam/' + jam_id)
        flash('Błąd: Nie ma takiego jamu')
        return redirect('jam/'+jam_id)
    else:
        flash("Błąd: Nie masz uprawnień", category='error')
        return redirect('team/'+team_name)


@app.route('/jam/<jam_id>/delete')
@login_required
def delete_jam(jam_id):
    try:
        if User.query.filter_by(username=session['username']).first().admin or Jam.query.filter_by(id=jam_id).first().master == session['username']:
            this_jam = Jam.query.filter_by(id=jam_id).first()
            if this_jam:
                messages=Message.query.filter_by(title="Prośba o dołączenie drużyny do jamu gamejam".replace("gamejam", this_jam.title), adresser=this_jam.master).all()
                if messages:
                    for message in messages:
                        db.session.delete(message)
                        db.session.commit()
                db.session.delete(this_jam)
                db.session.commit()
                flash("Usunięto jam!")
            return redirect("/jams")
        else:
            flash("Nie masz uprawnień")
            return redirect(url_for('homepage'))
    except Exception as error:
        flash(error)
        return redirect(url_for('homepage'))


@app.route('/jam/<jam_id>/close')
@login_required
def close_jam(jam_id):
    try:
       if User.query.filter_by(username=session['username']).first().admin or Jam.query.filter_by(id=jam_id).first().master == session['username']:
           this_jam = Jam.query.filter_by(id=jam_id).first()
           if this_jam:
               this_jam.active=False
               db.session.commit()
               flash("Zamknięto jam!")
           return redirect("/jams")

       else:
           flash("Nie masz uprawnień")
           return redirect(url_for('homepage'))
    except Exception as error:
        flash(error)
        return redirect(url_for('homepage'))



"""
Koniec jamów początek plików
"""


@app.route("/downloadhelp/<jam_id>", methods=['POST'])
@login_required
def downloadhelp(jam_id):
    files = Game.query.order_by(Game.id.asc()).all()
    user_member = False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        teams = Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member = False

    title = request.form.get('title')
    used_title = Game.query.filter_by(title=title).first()
    description = request.form.get('description')
    if used_title:
        flash('Ta nazwa gry jest już zajęta, proszę wybierz inną.')
        files = Game.query.order_by(Game.id.asc()).all()
        return render_template('download.html', files=files, organizer=organizer, admin=admin)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        this_jam = Jam.query.filter_by(id=jam_id).first()
        new_game = Game()
        new_game.title = title
        new_game.team = Team.query.filter_by(master=session['username']).first().name
        new_game.description = description
        new_game.jam = this_jam.title
        new_game.path = filename
        teamsxd = []
        for i in this_jam.teams:
            teamsxd.append(Team.query.filter_by(name=i).first())
        teamsxd.append(this_jam.title)
        team = Team.query.filter_by(master=session['username']).first().id
        team = Team.query.get(team)
        team.gameinjams = teamsxd
        db.session.add(new_game)
        db.session.commit()
        flash("Gra dodana!")
        gc.collect()
    files = Game.query.order_by(Game.id.asc()).all()
    return render_template('download.html', files=files, organizer=organizer, admin=admin, member=user_member, team_leader=team_leader)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class NewFile(Form):
    title = StringField('Nazwa gry:', [validators.Length(min=4, max=20)])
    description = TextAreaField('O grze:', [validators.Length(min=4, max=200)])
    file = FileField()


@app.route("/download/", methods=['GET', 'POST'])
@login_required
def download():
    """Lista plików do pobrania oraz upload"""
    files = Game.query.order_by(Game.id.asc()).all()
    user_member = False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        user_team = Team.query.filter_by(master=session['username']).first()
        if user_team:
            user_team = user_team.name
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        teams = Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member = False
        user_team = '!!!!!!!'
    if request.method == "POST":
        title = request.form.get('title')
        used_title = Game.query.filter_by(title=title).first()
        description = request.form.get('description')
        id = request.form.get('id')
        jam = request.form.get('jam')
        team = request.form.get('team')
        user_team = Team.query.filter_by(name=team).first().id
        user_team = Team.query.get(user_team).name
        if used_title:
            flash('Ta nazwa gry jest już zajęta, proszę wybierz inną.')
            files = Game.query.order_by(Game.id.asc()).all()
            return render_template('download.html', files=files, organizer=organizer, admin=admin)
        edit = Game.query.get(id)
        edit.title = title
        edit.team = team
        edit.description = description
        edit.jam = jam
        db.session.commit()
        flash("Edycja zakończona sukcesem!")
        gc.collect()
        files = Game.query.order_by(Game.id.asc()).all()
        return render_template('download.html', files=files, organizer=organizer, admin=admin, member=user_member,
                               team_leader=team_leader, user_team=user_team)
    return render_template('download.html', files=files, organizer=organizer, admin=admin, member=user_member,
                           team_leader=team_leader, user_team=user_team)


@app.route('/download/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

"""
Koniec obsługi plików, początek obsługi konta administratora
"""


@app.route("/admin/")
@login_required
def admin():
    """to samo co user info tylko dla admina"""
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    if User.query.filter_by(username=session['username']).first().admin:
        return render_template('admin.html', organizer=organizer, admin=admin, member=user_member, team_leader=team_leader)
    return redirect('/')

@app.route("/user_list")
@login_required
def user_list():
    """wyświetla listę użytkowników wraz z linkami dla adminów do edycji kont użytkowników"""
    """nie wyświetla użytkownika piotr"""
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    if User.query.filter_by(username=session['username']).first().admin:
        users=User.query.order_by(User.id.asc()).all()
        admini = 0
        for user in users:
            if user.admin:
                admini += 1
        return render_template('user_list.html', users=users, admini=admini, organizer=organizer, admin=admin, team_leader=team_leader)
    flash('Nie dla psa kiełbasa')
    return redirect('/')

@app.route('/admin/user/<int:id>')
@login_required
def user_control(id):
    """umożliwia adminowi kontrolę nad użytkownikiem"""
    """nie działa na użytkownia piotr"""
    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False
    if id != 1:
        if User.query.filter_by(username=session['username']).first().admin:
            user = User.query.filter_by(id=id).first()
            teams=Team.query.order_by(Team.id.asc()).all()
            return render_template('user_control.html', user=user, teams=teams, organizer=organizer, admin=admin, member=user_member, team_leader=team_leader)

@app.route('/give_admin/<int:id>')
@login_required
def give_admin(id):
    """daje admina użytkownikowi"""
    """może być uruchomiona tylko przez admina"""
    """nie działa na użytkownika piotr"""
    if id != 1:
        if User.query.filter_by(username=session['username']).first().admin and User.query.filter_by(
                id=id).first() and User.query.filter_by(id=id).first() != User.query.filter_by(
                username=session['username']).first():
            try:
                User.query.filter_by(id=id).first().admin = True
                User.query.filter_by(id=id).first().a = True
                db.session.commit()
                flash('Przekazano uprawnienia administratora użytkownikowi ' + str(
                    User.query.filter_by(id=id).first().username))
                return redirect('/user_list')
            except:
                return redirect('/')
    return redirect('/')

@app.route('/take_admin/<int:id>')
@login_required
def take_admin(id):
    """odbiera admina użytkownikowi"""
    """może być uruchomiona tylko przez admina"""
    """nie działa na użytkownika piotr"""
    if id != 1:
        if User.query.filter_by(username=session['username']).first().admin and User.query.filter_by(id=id).first():
            try:
                User.query.filter_by(id=id).first().admin = False
                User.query.filter_by(id=id).first().a = False
                db.session.commit()
                flash('Odebrano uprawnienia administratora użytkownikowi ' + str(
                    User.query.filter_by(id=id).first().username))
                return redirect('/user_list')
            except Exception as e:
                flash('Błąd: ' + str(e), 'danger')
                return redirect('/')
    return redirect('/')

@app.route('/change_admin')
@login_required
def change_admin():
    if User.query.filter_by(username=session['username']).first().a:
        try:
            user=User.query.filter_by(username=session['username']).first()
            if user.admin:
                user.admin=False
            else:
                user.admin=True

            db.session.commit()
            flash("zmieniono stan na " + str(User.query.filter_by(username=session['username']).first().admin))
            return redirect('/user/' + session['username'])
        except Exception as e:
            flash('Błąd: ' + str(e), 'danger')
            return redirect('/')
    return redirect('/')


"""
Koniec obsługi konta administratora, wyszukiwanie 
"""


@app.route('/search/', methods=['GET'])
def search():
    search = request.args.get('search').lower()
    jams=Jam.query.order_by(Jam.id.asc()).all()
    a=[]
    for jam in jams:
        jam1 = jam.title
        found=re.findall(r'.*search.*'.replace('search', search), jam1.lower())
        if len(found)==0 :
            a.append(jam)
    for i in a:
        jams.remove(i)

    steams = Team.query.order_by(Team.id.asc()).all()
    a=[]
    for steam in steams:
        steam1 = steam.name
        found=re.findall(r'.*search.*'.replace('search', search), steam1.lower())
        if len(found)==0:
            a.append(steam)
    for i in a:
        steams.remove(i)

    users = User.query.order_by(User.id.asc()).all()
    a=[]
    for user in users:
        user1 = user.username
        found=re.findall(r'.*search.*'.replace('search', search), user1.lower())
        if len(found)==0 :
            a.append(user)
    for i in a:
        users.remove(i)

    games = Game.query.order_by(Game.id.asc()).all()
    a = []
    for game in games:
        game1 = game.title
        found = re.findall(r'.*search.*'.replace('search', search), game1.lower())
        if len(found) == 0:
            a.append(game)
    for i in a:
        games.remove(i)

    user_member=False
    team_leader = False
    try:
        organizer = User.query.filter_by(username=session['username']).first().organizer
        team = Team.query.filter_by(master=session['username']).all()
        if team:
            team_leader = True
        admin = User.query.filter_by(username=session['username']).first().admin
        admin = User.query.filter_by(username=session['username']).first().admin
        teams=Team.query.order_by(Team.id.asc()).all()
        for t in teams:
            if session['username'] in t.contributors:
                user_member = True
    except KeyError:
        organizer = False
        admin = False
        user_member=False

    return render_template('search.html', organizer=organizer, admin=admin, member=user_member, team_leader=team_leader, sgames=games, sjams=jams, steams=steams, susers=users)







"""
koniec funkcji obsługujących zdarzenia zainicjowane celowo przez użytkownika
"""


@app.route('/clear/')
def clear():
    session.clear()
    return redirect('/')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.secret_key = "sekretny klucz"
