import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Task(SqlAlchemyBase, SerializerMixin):
    """SQL база данных задач"""
    __tablename__ = 'tasks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String)
    condition = sqlalchemy.Column(sqlalchemy.String)
    examples = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    less_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('lessons.id'))

    lesson = orm.relationship("Lesson", back_populates='task')
    solution = orm.relationship('Solution', back_populates='task')
