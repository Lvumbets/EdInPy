import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Solution(SqlAlchemyBase):
    """SQL база данных для решений"""
    __tablename__ = 'solutions'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    answer = sqlalchemy.Column(sqlalchemy.String)

    student_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("students.id"))
    task_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("tasks.id"))

    is_checked = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_solved = sqlalchemy.Column(sqlalchemy.Boolean, default=False)

    student = orm.relationship('Student')
    task = orm.relationship('Task')

    def __repr__(self):
        return f'{self.answer} {self.student_id} {self.task_id}'
