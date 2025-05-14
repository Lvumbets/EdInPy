from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.fields.simple import BooleanField
from wtforms.widgets.core import TextArea


class TaskForm(FlaskForm):
    """WTF форма для отправки решений задач"""
    code = StringField('Code', widget=TextArea())
    submit = SubmitField('Отправить')


class TaskAdd(FlaskForm):
    """WTF форма для добавления новой задачи"""
    title = StringField('Название')
    condition = StringField('Описание')
    examples = StringField('Примеры')

    submit = SubmitField('Добавить')


class TaskEdit(FlaskForm):
    """WTF форма для изменения задачи"""
    title = StringField('Название')
    condition = StringField('Описание')
    examples = StringField('Примеры')
    less_id = IntegerField('Принадлежащий урок')

    submit = SubmitField('Сохранить')


class CheckSolve(FlaskForm):
    is_solved = BooleanField('Решено ли?')
    submit = SubmitField('Сохранить')
