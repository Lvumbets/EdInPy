import sqlalchemy
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .db_session import SqlAlchemyBase
from static.config.users import USER_ADMIN


class Admin(SqlAlchemyBase, UserMixin, SerializerMixin):
    """SQL база данных для админов"""
    __tablename__ = "admins"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)

    access_level = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=1)  # уровень доступа админа

    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    image_name = sqlalchemy.Column(sqlalchemy.Text, nullable=True, unique=True)

    def __repr__(self):
        return '{surname} {name} is admin'.format(surname=self.surname, name=self.name)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_id(self):
        return f"{self.id}|{USER_ADMIN}"
