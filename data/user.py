import datetime
import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'user'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    nick = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    img_way = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    level = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=1)
    news = orm.relation("News", back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)