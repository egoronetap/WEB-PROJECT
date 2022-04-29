import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Form(SqlAlchemyBase):
    __tablename__ = 'form'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    img_way = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
