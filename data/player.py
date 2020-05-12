import datetime
import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy_serializer.serializer import SerializerMixin
from .db_session import SqlAlchemyBase, create_session


class Player(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'players'

    player_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    hashed_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    place = sqlalchemy.Column(sqlalchemy.String, default='last')
    points = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    public = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=False)
    online = sqlalchemy.Column(sqlalchemy.BOOLEAN, default=False)
    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    modifed_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f'<Player> {self.player_id} {self.surname} {self.name} {self.place} {self.points}'

    def get_id(self):
        return self.player_id

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def set_hashed_id(self):
        self.hashed_id = generate_password_hash(generate_password_hash(str(self.player_id)) +
                                                generate_password_hash('Terraria'))[22:]
