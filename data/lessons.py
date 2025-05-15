import sqlalchemy
from sqlalchemy import orm
# from sqlalchemy_serializer import SerializerMixin НЕКОННЕКТИТСЯ С GLITCH, В ОСТАЛЬНОМ ОСТАВИТЬ

from .db_session import SqlAlchemyBase


class Lesson(SqlAlchemyBase):  # SerializerMixin НЕ КОННЕКТИТСЯ С GLITCH, В ОСТАЛЬНОМ ДОБАВИТЬ
    """SQL база данных уроков"""
    __tablename__ = 'lessons'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)

    books = orm.relationship("LessonBook")
    task = orm.relationship("Task")
