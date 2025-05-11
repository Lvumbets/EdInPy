from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from flask_wtf.file import FileField, FileRequired
from wtforms.widgets import TextArea


class LessonBookParagraphAdd(FlaskForm):
    """WTF форма для добавления раздела учебника"""
    content = StringField('Содержимое', widget=TextArea())
    position = IntegerField('Номер по порядку в учебнике')

    submit = SubmitField('Добавить')


class LessonBookImageAdd(FlaskForm):
    """WTF форма для добавления изображения учебника"""
    image = FileField('Изображение', validators=[FileRequired()])
    position = IntegerField('Номер по порядку в учебнике')

    submit = SubmitField('Добавить')


class LessonBookParagraphEdit(FlaskForm):
    """WTF форма для редактирования раздела учебника"""
    content = StringField('Содержимое', widget=TextArea())
    position = IntegerField('Номер по порядку в учебнике')

    submit = SubmitField('Сохранить')


class LessonBookImageEdit(FlaskForm):
    """WTF форма для редактирования изображения учебника"""
    position = IntegerField('Номер по порядку в учебнике')

    submit = SubmitField('Сохранить')
