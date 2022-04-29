import sqlalchemy

from .db_session import SqlAlchemyBase


class Photos(SqlAlchemyBase):
    __tablename__ = 'photos'
    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    img_way = sqlalchemy.Column(sqlalchemy.String, nullable=False)