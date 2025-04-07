import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Learn(SqlAlchemyBase, UserMixin, SerializerMixin):
    '''SQL база данных уроков'''
    __tablename__ = 'learns'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String)
    condition = sqlalchemy.Column(sqlalchemy.String)

    examples = sqlalchemy.Column(sqlalchemy.String, nullable=True)
