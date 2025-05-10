from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField
from wtforms.widgets import TextArea


class LessonBookAdd(FlaskForm):
    """WTF форма для добавления нового учебника"""
    title = StringField('Название')
    description = StringField('Описание')
    text_template = StringField('Текст в формате HTML', widget=TextArea())

    submit = SubmitField('Добавить')


class LessonBookEdit(FlaskForm):
    """WTF форма для редактирования учебника"""
    title = StringField('Название')
    description = StringField('Описание')
    text_template = StringField('Текст в формате HTML')

    submit = SubmitField('Сохранить')
