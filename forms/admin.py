from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired


class LoginAdmin(FlaskForm):
    '''WTF форма для логина админов'''
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
