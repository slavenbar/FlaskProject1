from flask import Flask,render_template,url_for,request,flash,session,redirect,abort,g
import sqlite3
import os
from FDataBase import FDataBase

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path,'/tmp/flsite.db')))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    """Вспомогательная функция для создания таблиц БД"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()

#app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'
menu = [{'name':'Главная', 'url': 'main-app'},
        {'name':'Нейросеть', 'url': 'neuro-app'},
        {'name':'Обратная связь','url': 'contact'},
        {'name':'Регистрация','url': 'login'},
        {'name':'О нас','url': 'about'},
        {'name':'Добавить статью','url': 'add_post'}]

@app.route('/')
def index():
    return render_template('index.html', title='Искусственный интеллект на связи!', menu=menu)

@app.route('/profile/main-app')
def main_app():
    if 'userLogged' in session:

        return render_template('index.html', title='Искусственный интеллект на связи!', menu=menu)

@app.route('/profile/neuro-app')
def neuro_app():
    return render_template('neuroindex.html', title='Здравствуй человек!', menu=menu)

@app.route('/profile/about')
def about():
    return render_template('about.html', title='Мы в ай ти', menu=menu)


@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    db = get_db()
    dbase = FDataBase(db)

    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'])
            if not res:
                flash('Ошибка добавления статьи', category='error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')

    return render_template('add_post.html', menu=dbase.getMenu(), title="Добавление статьи")

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

@app.route("/login", methods=["POST", "GET"])
def login():
    print(url_for('login'))
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.form.get('username') and request.form.get('psw') :
        session['userLogged'] = request.form.get('username')
        return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title="Авторизация", menu=menu)

@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена", menu=menu)


if __name__ == '__main__':
    app.run(debug=True)