from flask_wtf import FlaskForm
from wtforms import SubmitField


class NotificationRead(FlaskForm):
    """WTF форма для чтения уведомления"""
    submit = SubmitField('Прочитать')


class NotificationReadAll(FlaskForm):
    """WTF форма для чтения уведомления"""
    submit = SubmitField('Прочитать все')
