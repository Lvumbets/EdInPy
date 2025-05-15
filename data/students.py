import sqlalchemy
from flask_login import UserMixin, current_user
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

from static.config.users import USER_STUDENT
from .db_session import SqlAlchemyBase, create_session
from .student_notifications import StudentNotification


class Student(SqlAlchemyBase, UserMixin):
    """SQL база данных для учеников"""
    __tablename__ = 'students'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    surname = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    age = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    email = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)

    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    completed_tasks = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    teacher_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("teachers.id"))

    teacher = orm.relationship('Teacher', back_populates='student')
    task = orm.relationship('Solution', back_populates='student')

    image_name = sqlalchemy.Column(sqlalchemy.Text, nullable=True, unique=True)

    def has_notifications(self):
        with create_session() as db_sess:
            result = db_sess.query(StudentNotification).filter(StudentNotification.student_id == current_user.id,
                                                               StudentNotification.is_read == False).first()
            return result is not None

    def __repr__(self):
        return '{surname} {name}'.format(surname=self.surname, name=self.name)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_id(self):
        return f"{self.id}|{USER_STUDENT}"
