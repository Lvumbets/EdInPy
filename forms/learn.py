from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.widgets.core import TextArea


class LearnForm(FlaskForm):
    code = StringField('Code', widget=TextArea())
    submit = SubmitField('Отправить')
