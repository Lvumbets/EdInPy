import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase


class Student(SqlAlchemyBase, UserMixin, SerializerMixin):
    '''SQL база данных для учеников'''
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)

    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"))

    teacher = orm.relationship('Teacher', back_populates='student')
    task = orm.relationship('Solution', back_populates='student')

    def __repr__(self):
        return '{surname} {name}'.format(surname=self.surname, name=self.name)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
