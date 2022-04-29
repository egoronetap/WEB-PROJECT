from flask import Flask, render_template, request, redirect, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.exceptions import abort
from werkzeug.security import generate_password_hash, check_password_hash

from data import db_session
from data.__all_models import *

import requests

import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'very_secret_key'
app.config['IMAGE_UPLOADS'] = 'C:\\Projects\\Python\\WEB-PROJECT\\static\\img'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/site.db")

MODERATOR = 2
USER = 1
API = '882b91c9-a9e2-4d23-b79f-172ff50f0108'


@app.route('/')
@app.route('/index')
def index():
    name = 'Главная страница'
    visits_count = session.get('visits_count', 0)
    visits = visits_count
    session['visits_count'] = visits_count + 1
    return render_template('main.html', title=name, visits_count=visits)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        req = request.form
        image = request.files['img_way']
        db_sess = db_session.create_session()
        if not req['name']:
            return render_template('register.html', message='Вы не ввели свое имя')
        elif not req['surname']:
            return render_template('register.html', message='Вы не ввели свою фамилию')
        elif not req['email']:
            return render_template('register.html', message='Вы не ввели свою почту')
        elif not req['password']:
            return render_template('register.html', message='Вы не ввели пароль')
        elif not req['second_password']:
            return render_template('register.html', message='Вы не подтвердили пароль')
        elif not req['nick']:
            return render_template('register.html', message='Вы не ввели псевдоним')
        elif req['password'] != req['second_password']:
            return render_template('register.html', message='Пароли не совпадают')
        elif db_sess.query(User).filter(User.nick == req['nick']).first():
            return render_template('register.html', message='Псевдоним уже занят')
        elif image.filename.split('.')[-1] not in ['png', 'PNG', 'JPG', 'jpg', 'JPEG', 'jpeg']:
            return render_template('register.html', message='Неправильный формат фотографии')
        user = User(name=req['name'], surname=req['surname'], nick=req['nick'],
                    description=req['description'], email=req['email'],
                    password=generate_password_hash(req['password']))
        if image:
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], str(image).split("'")[1].split()[-1]))
            user.img_way = str(image).split("'")[1].split()[-1]
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = Log()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('login.html', message='Неправильный логин или пароль', form=form)
    return render_template('login.html', form=form)


@app.route('/check_photo', methods=['POST', 'GET'])
def check_photo():
    db_sess = db_session.create_session()
    lst = []
    for photo in db_sess.query(Photos).all():
        lst.append(photo.img_way)
    if request.method == 'POST':
        if 'add_photo' in request.form:
            if not db_sess.query(AcceptedPhotos).filter(AcceptedPhotos.img_way == lst[0]).first():
                acc_photo = AcceptedPhotos(img_way=lst[0])
                db_sess.delete(db_sess.query(Photos).first())
                db_sess.add(acc_photo)
                db_sess.commit()
                return redirect('/check_photo')
            db_sess.delete(db_sess.query(Photos).first())
            db_sess.commit()
            return redirect('/check_photo')
        elif 'delete_photo' in request.form:
            db_sess.delete(db_sess.query(Photos).first())
            db_sess.commit()
            return redirect('/check_photo')
    return render_template('check_photo.html', lst=lst)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/<user_name>', methods=['POST', 'GET'])
def user_page(user_name):
    return render_template('user_page.html')


@app.route('/album', methods=['POST', 'GET'])
def album():
    name = 'Альбом'
    db_sess = db_session.create_session()
    lst = []
    for photo in db_sess.query(AcceptedPhotos).all():
        lst.append(photo.img_way)
    if request.method == 'POST':
        if request.files['img_way']:
            image = request.files['img_way']
            if image.filename.split('.')[-1] not in ['png', 'PNG', 'JPG', 'jpg', 'JPEG', 'jpeg']:
                return render_template('album.html', title=name, message='Неправильный формат фотографии', lst=lst)
            image.save(os.path.join(app.config['IMAGE_UPLOADS'], image.filename))
            photo = Photos(img_way=str(image).split("'")[1])
            db_sess = db_session.create_session()
            db_sess.add(photo)
            db_sess.commit()
            return render_template('album.html', title=name, message='Фотография отправлена на проверку', lst=lst)
        return render_template('album.html', title=name, message='Вы не загрузили фотографию', lst=lst)
    return render_template('album.html', title=name, lst=lst)


@app.route('/add_news',  methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/forum')
    return render_template('add_news.html', title='Добавление новости',
                           form=form)


@app.route("/forum")
def forum():
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.is_private != True)
    return render_template("forum.html", news=news)


@app.route('/add_news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/forum')
        else:
            abort(404)
    return render_template('add_news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/news_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id,
                                      News.user == current_user
                                      ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/forum')


@app.route('/map')
def show_map():
    return render_template('map.html')


@app.route('/timetable')
def timetable():
    params = {'apikey': API,
              'from': 's2000006',
              'to': 's9601890'
              }
    response = requests.get('https://api.rasp.yandex.net/v3.0/search/', params)
    dct_to = [response.json()['segments'][0]]
    params = {'apikey': API,
              'from': 's9601890',
              'to': 's2000006'
              }
    response = requests.get('https://api.rasp.yandex.net/v3.0/search/', params)
    dct_from = [response.json()['segments'][0]]
    print(response.json()['segments'][0]['departure'])
    return render_template('timetable.html', dct_from=dct_from, dct_to=dct_to)


if __name__ == '__main__':
    app.run(debug=True)
