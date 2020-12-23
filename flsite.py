from flask import Flask,render_template,url_for,request,flash,session,redirect,abort,g
import sqlite3
import os
from FDataBase import FDataBase
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"


class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    old = db.Column(db.Integer)
    city = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<profiles {self.id}>"

#Закоментировать код ctrl+/
app.config.from_object(__name__)

#app.config.update(dict(DATABASE=os.path.join(app.root_path,'/tmp/flsite.db')))

# def connect_db():
#     conn = sqlite3.connect(app.config['DATABASE'])
#     conn.row_factory = sqlite3.Row
#     return conn

# def create_db():
#     """Вспомогательная функция для создания таблиц БД"""
#     db = connect_db()
#     with app.open_resource('sq_db.sql', mode='r') as f:
#         db.cursor().executescript(f.read())
#     db.commit()
#     db.close()
#
# def get_db():
#     '''Соединение с БД, если оно еще не установлено'''
#     if not hasattr(g, 'link_db'):
#         g.link_db = connect_db()
#     return g.link_db
#
# @app.teardown_appcontext
# def close_db(error):
#     '''Закрываем соединение с БД, если оно было установлено'''
#     if hasattr(g, 'link_db'):
#         g.link_db.close()

app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'
menu = [{'name':'Главная', 'url': 'main-app'},
        {'name':'Нейросеть', 'url': 'neuro-app'},
        {'name':'Обратная связь','url': 'contact'},
        {'name':'Регистрация','url': 'login'},
        {'name':'О нас','url': 'about'},
        {'name':'Добавить статью','url': 'add_post'}]

@app.route('/')
def index():
    return render_template('index.html', title='Искусственный интеллект на связи!', menu=menu)

@app.route('/main-app')
def main_app():
        return render_template('index.html', title='Искусственный интеллект на связи!', menu=menu)

@app.route('/profile/neuro-app')
def neuro_app():
    return render_template('neuroindex.html', title='Здравствуй человек!', menu=menu)

@app.route('/profile/about')
def about():
    return render_template('about.html', title='Мы в ай ти', menu=menu)


# @app.route("/add_post", methods=["POST", "GET"])
# def addPost():
#     db = get_db()
#     dbase = FDataBase(db)
#
#     if request.method == "POST":
#         if len(request.form['name']) > 4 and len(request.form['post']) > 10:
#             res = dbase.addPost(request.form['name'], request.form['post'])
#             if not res:
#                 flash('Ошибка добавления статьи', category='error')
#             else:
#                 flash('Статья добавлена успешно', category='success')
#         else:
#             flash('Ошибка добавления статьи', category='error')
#
#     return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")

#Пользователь отправляет сообщение на сайт

@app.route('/contact', methods=['POST','GET'])
def contact():
    if request.method == 'POST':
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template('contact.html', title='Обратная связь', menu=menu)


@app.route("/profile/<username>")
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    else:
        return render_template('registry.html', title=f'Вы зарегались : {username}', menu=menu)


# @app.route("/login", methods=["POST", "GET"])
# def login():
#     if 'userLogged' in session:
#         return redirect(url_for('profile', username=session['userLogged']))
#     elif request.form.get('username') and request.form.get('psw') :
#         session['userLogged'] = request.form.get('username')
#         return redirect(url_for('profile', username=session['userLogged']))
#
#     return render_template('login.html', title="Авторизация", menu=menu)
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        # здесь должна быть проверка корректности введенных данных
        try:
            hash = generate_password_hash(request.form['psw'])
            u = Users(email=request.form['email'], psw=hash)
            db.session.add(u)
            db.session.flush()

            p = Profiles(name=request.form['name'], old=request.form['old'],
                         city=request.form['city'], user_id=u.id)
            db.session.add(p)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")
        return redirect("main-app")
    return render_template("login.html", title="Регистрация",menu=menu)

#Повторный вход в регистрацию
@app.route("/profile/login")
def profile2():
        return render_template('registry.html', title=f'Вы зарегистрировались : {"товарищ"}', menu=menu)



#Декоратор для отправки ошибки
@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu)


if __name__ == '__main__':
    app.run(debug=True)