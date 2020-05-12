from data import db_session
from flask_restful import Api
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required
from data.register import RegisterForm
from data.LoginForm import LoginForm
from data.RedactForm import RedactForm
from data.player import Player
from data.players_resources import PlayerResource, PlayersListResource
import logging


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
api = Api(app)

'''logging.basicConfig(level=logging.INFO, filename='logs.log',
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')'''
loaded_player = [None]


def main():
    db_session.global_init("db/players.sqlite")
    app.config['JSON_AS_ASCII'] = False
    api.add_resource(PlayerResource, '/api/players/<int:player_id>')
    api.add_resource(PlayersListResource, '/api/players')

    @app.route("/")
    def index():
        session = db_session.create_session()
        players = session.query(Player).filter(Player.public is True).all()
        names = {name.player_id: (name.nickname, name.place, name.points, name.online) for name in players}
        return render_template("index.html", players=names, title="Game Status")

    @app.route("/<string:hashed_id>")
    @login_required
    def index_plus(hashed_id):
        session = db_session.create_session()
        players = session.query(Player).filter(Player.public is True or Player.hashed_id == hashed_id).all()
        names = {name.player_id: (name.nickname, name.place, name.points, name.online) for name in players}
        return render_template("index.html", players=names, title="Game Status")

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            if form.password.data != form.password_again.data:
                return render_template('register.html', title='Регистрация', form=form,
                                       message="Пароли не совпадают")
            session = db_session.create_session()
            if session.query(Player).filter(Player.email == form.email.data).first():
                return render_template('register.html', title='Регистрация', form=form,
                                       message="Такой пользователь уже есть")
            player = Player(
                name=form.name.data,
                email=form.email.data,
                surname=form.surname.data,
                nickname=form.nickname.data,
                public=form.public.data
            )
            player.set_password(form.password.data)
            player.set_hashed_id()
            session.add(player)
            session.commit()
            return redirect('/login')
        return render_template('register.html', title='Регистрация', form=form)

    @app.route("/redact", methods=['GET', 'POST'])
    @login_required
    def redact():
        global loaded_player
        form = RedactForm()
        session = db_session.create_session()
        player = session.query(Player).filter(Player.hashed_id == loaded_player[0]).first()
        if form.validate_on_submit():
            if not player.check_password(form.old_password.data):
                return render_template('redact.html', title='Редактировать информацию о себе', form=form,
                                       message='Некорректный старый пароль')
            if form.password.data != form.password_again.data:
                return render_template('redact.html', title='Редактировать информацию о себе', form=form,
                                       message="Пароли не совпадают")
            player = Player(
                name=form.name.data,
                surname=form.surname.data,
                nickname=form.nickname.data,
                public=form.public.data
            )
            player.set_password(form.password.data)
            session.add(player)
            session.commit()
            return redirect('/login')
        return render_template('redact.html', title='Редактировать информацию о себе', form=form)

    @login_manager.user_loader
    def load_user(player_id):
        session = db_session.create_session()
        return session.query(Player).get(player_id)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        global loaded_player
        form = LoginForm()
        if form.validate_on_submit():
            session = db_session.create_session()
            player = session.query(Player).filter(Player.email == form.email.data).first()
            if player and player.check_password(form.password.data):
                login_user(player, remember=form.remember_me.data)
                loaded_player = [player.hashed_id]
                player.online = True
                session.commit()
                print(loaded_player)
                return redirect(f"/{player.hashed_id}")
            return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
        return render_template('login.html', title='Авторизация', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        global loaded_player
        session = db_session.create_session()
        player = session.query(Player).filter(Player.hashed_id == loaded_player[0]).first()
        player.online = False
        loaded_player = [None]
        session.commit()
        logout_user()
        return redirect("/")

    app.run(debug=True)


if __name__ == '__main__':
    main()
