from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField
from wtforms.fields.simple import BooleanField
from wtforms.validators import DataRequired


class RegisterTeacher(FlaskForm):
    '''WTF форма для регистрации учителей'''
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    age = StringField('Возраст', validators=[DataRequired()])

    students = StringField('Ученики (узнайте id у своих учеников и введите их через пробел)')

    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])

    access_code = StringField('Код учителя', validators=[DataRequired()])

    submit = SubmitField('Зарегистрироваться')


class LoginTeacher(FlaskForm):
    '''WTF форма для авторизации учителя'''
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class ChangeStudents(FlaskForm):
    '''WTF форма для изменения учеников учителя'''
    students = StringField('Ученики (напишите их id через пробел)')
    submit = SubmitField('Сохранить')