from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class LessonAdd(FlaskForm):
    '''WTF форма для добавления нового урока'''
    title = StringField('Название')
    description = StringField('Описание')

    submit = SubmitField('Сохранить')


class LessonEdit(FlaskForm):
    '''WTF форма для редактирования урока'''
    title = StringField('Название')
    description = StringField('Описание')

    submit = SubmitField('Отправить')
