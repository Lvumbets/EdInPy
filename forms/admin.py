from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField
from wtforms.fields.simple import BooleanField, StringField
from wtforms.validators import DataRequired


class RegisterAdmin(FlaskForm):
    '''WTF форма для регистрации учителей'''
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    age = StringField('Возраст', validators=[DataRequired()])

    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])

    access_code = StringField('Код админа', validators=[DataRequired()])

    submit = SubmitField('Зарегистрироваться')


class LoginAdmin(FlaskForm):
    '''WTF форма для логина админов'''
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
