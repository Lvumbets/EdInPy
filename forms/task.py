from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import BooleanField
from wtforms.widgets.core import TextArea


class TaskForm(FlaskForm):
    '''WTF форма для отправки решений задач'''
    code = StringField('Code', widget=TextArea())
    submit = SubmitField('Отправить')


class CheckSolve(FlaskForm):
    is_solved = BooleanField('Решено ли?')
    submit = SubmitField('Сохранить')
