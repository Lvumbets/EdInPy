import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Lesson(SqlAlchemyBase, UserMixin, SerializerMixin):
    '''SQL база данных уроков'''
    __tablename__ = 'lessons'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String)

    task = orm.relationship("Task")
