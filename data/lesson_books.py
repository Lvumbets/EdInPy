import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class LessonBook(SqlAlchemyBase):
    """SQL база данных уроков"""
    __tablename__ = 'lesson_books'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String)

    lesson_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lessons.id"), nullable=False)

    paragraphs = orm.relationship('LessonBookParagraph', backref='lesson_books', passive_deletes=True)
