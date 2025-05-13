from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField
from flask_wtf.file import FileField, FileRequired


class ProfileImageAdd(FlaskForm):
    """WTF форма для добавления изображения профиля"""
    image = FileField('Изображение', validators=[FileRequired()])
    name = StringField('Имя')
    surname = StringField('Фамилия')
    age = IntegerField("Возраст")

    submit = SubmitField('Сохранить')
