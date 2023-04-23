import json
import os
import random

from flask import Flask, render_template, redirect, session, make_response, request, abort, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

import functions
from forms.user import RegisterForm, LoginForm, EmergencyAccessForm
from data.jobs import Jobs
from data.users import User
from data.departaments import Departament
from data import db_session, jobs_api, user_api
from forms.jobsForm import JobsForm
from forms.departamentForm import DepartamentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexLyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/MarsOne.db")
    app.register_blueprint(jobs_api.blueprint)
    app.register_blueprint(user_api.blueprint)
    app.run()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    names = []
    leaders = []
    for job in jobs:
        ids = job.collaborators.split(', ')
        users = ', '.join([db_sess.query(User).filter(User.id == i)[0].name for i in ids])
        names.append(users)
        leader = db_sess.query(User).filter(User.id == job.team_leader)[0]
        leaders.append(leader.name)
    return render_template("index.html", jobs=jobs, names=names, len=len(names), leaders=leaders)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация', form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            address=form.address.data,
            speciality=form.speciality.data,
            city_from=form.city_from.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/emergency_access', methods=['GET', 'POST'])
def emergency_access():
    form = EmergencyAccessForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).get(form.id.data)
        cap = db_sess.query(User).get(form.id_cap.data)
        if user and user.check_password(form.password.data) and cap.check_password(form.password_cap.data):
            login_user(user)
            return redirect("/")
        return render_template('emergency_access.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('emergency_access.html', title='Авторизация', form=form)


@app.route('/distribution')
def distribution():
    db_sess = db_session.create_session()
    cap = db_sess.query(User).filter(User.position == 'капитан корабля').first()
    _list = db_sess.query(User).all()
    return render_template('distribution.html', _list=_list, cap=cap)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/jobs', methods=['GET', 'POST'])
@login_required
def add_jobs():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = Jobs()
        jobs.user = current_user
        jobs.job = form.job.data
        jobs.work_size = form.work_size.data
        jobs.collaborators = form.collaborators.data
        jobs.start_date = form.start_date.data
        jobs.is_finished = form.is_finished.data
        current_user.jobs.append(jobs)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('jobs.html', title='Добавление новости',
                           form=form)


@app.route('/jobs/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_jobs(id):
    form = JobsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                          Jobs.user == current_user
                                          ).first()
        if jobs:
            form.is_finished.data = jobs.is_finished
            form.start_date.data = jobs.start_date
            form.collaborators.data = jobs.collaborators
            form.work_size.data = jobs.work_size
            form.job.data = jobs.job
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                          Jobs.user == current_user
                                          ).first()
        if jobs:
            jobs.job = form.job.data
            jobs.work_size = form.work_size.data
            jobs.collaborators = form.collaborators.data
            jobs.start_date = form.start_date.data
            jobs.is_finished = form.is_finished.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('jobs.html',
                           title='Редактирование работы',
                           form=form
                           )


@app.route('/jobs_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).filter(Jobs.id == id,
                                      Jobs.user == current_user
                                      ).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/users_show/<int:id_user>', methods=['GET', 'POST'])
def get_user_city(id_user):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(id_user)
    if user:
        return render_template('image_city.html',
                               city_url=functions.geocoder(user.city_from),
                               user=user
                               )
    else:
        abort(404)
    return redirect('/')


@app.route("/departament")
def depart():
    db_sess = db_session.create_session()
    departament = db_sess.query(Departament).all()
    names = []
    leaders = []
    for dep in departament:
        ids = dep.members.split(', ')
        users = ', '.join([db_sess.query(User).filter(User.id == i)[0].name for i in ids])
        names.append(users)
        leader = db_sess.query(User).filter(User.id == dep.chief)[0]
        leaders.append(leader.name)
    return render_template("departamentList.html", jobs=departament, names=names, len=len(names), leaders=leaders)


@app.route('/add_departament', methods=['GET', 'POST'])
@login_required
def add_departament():
    form = DepartamentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        departament = Departament(user=current_user,
                                  title=form.title.data,
                                  chief=form.chief.data,
                                  members=form.members.data,
                                  email=form.email.data)
        current_user.departament.append(departament)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/departament')
    return render_template('departament.html', title='Добавление департамента',
                           form=form)


@app.route('/departament/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_departament(id):
    form = DepartamentForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        departament = db_sess.query(Departament).filter(Departament.id == id,
                                                        Departament.user == current_user).first()
        if departament:
            form.title.data = departament.title
            form.chief.data = departament.chief
            form.members.data = departament.members
            form.email.data = departament.email
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        departament = db_sess.query(Departament).filter(Departament.id == id,
                                                        Departament.user == current_user
                                                        ).first()
        if departament:
            departament.title = form.title.data
            departament.chief = form.chief.data
            departament.members = form.members.data
            departament.email = form.email.data
            db_sess.commit()
            return redirect('/departament')
        else:
            abort(404)
    return render_template('departament.html',
                           title='Редактирование департамента',
                           form=form
                           )


@app.route('/departament_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def departament_delete(id):
    db_sess = db_session.create_session()
    departament = db_sess.query(Departament).filter(Departament.id == id,
                                                    Departament.user == current_user
                                                    ).first()
    if departament:
        db_sess.delete(departament)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/departament')


@app.route('/form_sample', methods=['GET', 'POST'])
def form_sample():
    if request.method == 'GET':
        images = ['static/img/' + filename for filename in os.listdir('static/img')]
        return render_template('images_slider.html', images=images, _len=len(images))
    elif request.method == 'POST':
        f = request.files['file']
        f.save(os.path.join('static', 'img', f"{request.files['file'].filename}"))
        return redirect('/form_sample')


@app.route('/member')
def member():
    with open('templates/crew.json', encoding='utf-8') as file:
        users = json.load(file)
    user = random.choice(users)
    user['speciality'] = ', '.join(sorted(user['speciality']))
    return render_template('card.html', user=user)


@app.route('/table/<string:gender>/<int:age>')
def table(gender, age):
    return render_template('room.html', gender=gender, age=age)


def create_json():
    result = []
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    for user in users:
        result.append({'name': user.name,
                       'surname': user.surname,
                       'speciality': user.speciality.split(','),
                       'img': '/static/img/1.png'

                       })
    with open('templates/crew.json', 'w', encoding='utf-8') as file:
        json.dump(result, file)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


if __name__ == '__main__':
    main()
