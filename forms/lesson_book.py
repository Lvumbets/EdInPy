from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class LessonBookAdd(FlaskForm):
    """WTF форма для добавления нового учебника"""
    title = StringField('Название')
    description = StringField('Описание')

    submit = SubmitField('Добавить')


class LessonBookEdit(FlaskForm):
    """WTF форма для редактирования учебника"""
    title = StringField('Название')
    description = StringField('Описание')

    submit = SubmitField('Сохранить')
