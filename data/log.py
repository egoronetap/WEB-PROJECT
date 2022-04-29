import sqlalchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from .db_session import SqlAlchemyBase


class Log(FlaskForm):
    __tablename__ = 'log'
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
