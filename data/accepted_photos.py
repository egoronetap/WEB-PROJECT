import sqlalchemy

from .db_session import SqlAlchemyBase


class AcceptedPhotos(SqlAlchemyBase):
    __tablename__ = 'accepted_photos'
    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    img_way = sqlalchemy.Column(sqlalchemy.String, nullable=False)
