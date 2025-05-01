from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.widgets.core import TextArea


class TaskForm(FlaskForm):
    '''WTF форма для отправки решений задач'''
    code = StringField('Code', widget=TextArea())
    submit = SubmitField('Отправить')
