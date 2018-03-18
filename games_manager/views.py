"""w budowie sqlalchemmy"""
import os
from main import app
from main import db
from main import bcrypt
from main import lm
from models import User, Team, Message
import gc
from passlib.hash import sha256_crypt
from functools import wraps
from flask import Flask, render_template, flash, request, redirect, url_for, session, send_from_directory
from wtforms import Form, validators, StringField, PasswordField, BooleanField
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
        if 'logged_in' in session:
            return func(*args, **kwargs)
        flash("Musisz być zalogowany.")

    return wrap


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
    job = StringField('Czym się zajmujesz')
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
            user.email = email
            user.password = password
            user.username = username
            user.job = job
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
        User.query.filter_by(username=session['username']).first().active = 0
        db.session.commit()
        session.clear()
        flash("Zostałeś poprawnie wylogowany.")
        gc.collect()
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
    return render_template('main.html')


@app.route("/info/")
def info():
    return render_template("info.html")


"""
Koniec podstawowych informacji o stronie, początek informacji o użytkowniku
"""


@app.route('/user/<username>')
def user_info_id(username):
    """
    Tu będą wyświetlane gamejamy, drużyny, gry i dokłade dane dotyczące użytkownika
    """
    user=User.query.filter_by(username=username).first()
    user_teams=Team.query.filter_by(master=username).all()
    teams = Team.query.order_by(Team.id.asc()).all()
    admin=User.query.filter_by(username=session['username']).first().admin
    return render_template('user_info.html', job=User.query.filter_by(username=session['username']).first().job, user=user, admin=admin, teams=teams,teams2=user_teams)

@app.route('/user/<username>/messages')
def user_messages(username):
    if session['username']==username or User.query.filter_by(username=session['username']).first().admin:

        messages=Message.query.filter_by(adresser=username).all()
        try:
            if messages:
                return render_template('user_messages.html', messages=messages, )
            return redirect('/')
        except:
            return redirect('/')

@app.route('/message/<id>')
def message_print(id):
    if session['username'] == Message.query.filter_by(id=id).first().adresser or User.query.filter_by(username=session['username']).first().admin:
        message=Message.query.filter_by(id=id).first()
        message.new=False
        db.session.commit()
        return render_template("message_normal.html", message=message)
    return redirect("/")


"""
Koniec informacji o użytkowniku, początek usuwania użytkownika
"""


@app.route('/delete/<int:id>')
def delete(id):
    """NIE DZIAłA NA UŻYTKOWNIKA PIOTR"""
    """Funkcja usuwa użytkownika, po czym jeżeli zalogoway użytkownik to admin, zwraca listę użytkowników, w przeciwnym przypadku wraca na stronę główną"""
    if id == User.query.filter_by(username=session['username']).first().id or User.query.filter_by(
            username=session['username']).first().admin:
        user = User.query.filter_by(id=id).first()

        if user:
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


@app.route("/team/<team_name>")
def team(team_name):
    """wyświetla informacje o drużynie"""
    this_team = Team.query.filter_by(name=team_name).first()
    admin = User.query.filter_by(username=session['username']).first().admin
    if this_team:
        return render_template("team.html", team=this_team, admin=admin)
    return render_template('404.html'), 404

class NewTeamForm(Form):
    name = StringField('Nazwa zespołu', [validators.Length(min=4, max=20)])


@app.route('/create-team/', methods=["GET", "POST"])
@login_required
def create_team():
    if session['logged_in']==True:
        try:
            form = NewTeamForm(request.form)
            if request.method == "POST" and form.validate():
                name = form.name.data
                used_name = Team.query.filter_by(name=name).first()
                if used_name:
                    flash('Ta nazwa użytkowania jest już zajęta, proszę wybierz inną.')
                    return render_template('create-team.html', form=form)
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
            return render_template('create-team.html', form=form)
        except Exception as error:
            flash(error)
            return redirect(url_for('homepage'))
    else:
        flash("Musisz być zalogowany")
        return redirect(url_for('homepage'))

@app.route('/delete-team/<team_name>')
@login_required
def delete_team(team_name):
    if session['logged_in']==True:
        try:
           if User.query.filter_by(username=session['username']).first().admin:
               this_team = Team.query.filter_by(name=team_name).first()
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
    else:
        flash("Musisz być zalogowany")
        return redirect(url_for('homepage'))

@app.route('/team/<team_name>/invite', methods=['GET','POST'])
def invite_redirect(team_name):
    if request.method=='GET':
        return render_template('team.html')
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
def team_invite(team_name,username):
    if User.query.filter_by(username=session['username']).first().admin or Team.query.filter_by(name=team_name).first().master==session['username']:
        new_message = Message()
        new_message.title ="Zaproszenie do drużyny "+team_name
        new_message.author =Team.query.filter_by(name=team_name).first().master
        new_message.adresser =username
        new_message.created=datetime.now()
        new_message.content = "Zostałeś zaproszony do drużyny "+team_name+". W tej drużynie znajdują się: "+str(Team.query.filter_by(name=team_name).first().contributors)
        db.session.add(new_message)
        db.session.commit()
        flash("użytkownik został zaproszony")
        return redirect('/team/'+team_name)
    return redirect("/")


@app.route('/team/<team_name>/join/<username>')
def team_join(team_name, username):
    if User.query.filter_by(username=session['username']).first().admin or Message.query.filter_by(title="Zaproszenie do drużyny "+team_name, adresser=username).first().adresser==username:
        if not username in Team.query.filter_by(name=team_name).first().contributors:
            team=Team.query.filter_by(name=team_name).first()
            cont=team.contributors[:]
            cont.append(username)
            team.contributors=cont[:]
            db.session.commit()
            flash('Pomyślnie dołączono do drużyny')
        return redirect('/team/'+team_name)
    return redirect('/')


"""
Koniec obsługi drużyn, początek obsługi plików
"""


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/download", methods=['GET', 'POST'])
def download():
    """Lista plików do pobrania oraz upload"""
    """ROZłOŻYć NA OSOBNY DOWNLOAD I UPLOAD"""
    files = os.listdir(UPLOAD_FOLDER)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download',
                                    files=files))
    return render_template('download.html', files=files)

@app.route('/download/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


"""
Koniec obsługi plików, początek obsługi konta administratora
"""


@app.route("/admin")
def admin():
    """to samo co user info tylko dla admina"""
    if User.query.filter_by(username=session['username']).first().admin:
        return render_template('admin.html')
    return redirect('/')

@app.route("/user_list")
def user_list():
    """wyświetla listę użytkowników wraz z linkami dla adminów do edycji kont użytkowników"""
    """nie wyświetla użytkownika piotr"""
    if User.query.filter_by(username=session['username']).first().admin:
        users=User.query.order_by(User.id.asc()).all()
        return render_template('user_list.html', users=users)
    flash('Nie dla psa kiełbasa')
    return redirect('/')

@app.route('/admin/user/<int:id>')
def user_control(id):
    """umożliwia adminowi kontrolę nad użytkownikiem"""
    """nie działa na użytkownia piotr"""
    if id != 1:
        if User.query.filter_by(username=session['username']).first().admin:
            user = User.query.filter_by(id=id).first()
            teams=Team.query.order_by(Team.id.asc()).all()
            return render_template('user_control.html', user=user, teams=teams)

@app.route('/give_admin/<int:id>')
def give_admin(id):
    """daje admina użytkownikowi"""
    """może być uruchomiona tylko przez admina"""
    """nie działa na użytkownika piotr"""
    if id != 1:
        if User.query.filter_by(username=session['username']).first().admin and User.query.filter_by(
                id=id).first() and User.query.filter_by(id=id).first() != User.query.filter_by(
                username=session['username']).first():
            try:
                User.query.filter_by(id=id).first().admin = 1
                db.session.commit()
                flash('Przekazano uprawnienia administratora użytkownikowi ' + str(
                    User.query.filter_by(id=id).first().username))
                return redirect('/user_list')
            except:
                return redirect('/')
    return redirect('/')

@app.route('/take_admin/<int:id>')
def take_admin(id):
    """odbiera admina użytkownikowi"""
    """może być uruchomiona tylko przez admina"""
    """nie działa na użytkownika piotr"""
    if id != 1:
        if User.query.filter_by(username=session['username']).first().admin and User.query.filter_by(id=id).first():
            try:
                User.query.filter_by(id=id).first().admin = 0
                db.session.commit()
                flash('Odebrano uprawnienia administratora użytkownikowi ' + str(
                    User.query.filter_by(id=id).first().username))
                return redirect('/user_list')
            except:
                return redirect('/')
    return redirect('/')


"""
Koniec obsługi konta administratora, koniec funkcji obsługujących zdarzenia zainicjowane celowo przez użytkownika
"""


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.secret_key = "sekretny klucz"