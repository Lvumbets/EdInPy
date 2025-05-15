import sqlalchemy

from .db_session import SqlAlchemyBase

PARAGRAPH_TYPE_IMAGE = "image"
PARAGRAPH_TYPE_TEXT = "text"


class LessonBookParagraph(SqlAlchemyBase):
    """SQL база данных разделов урока"""
    __tablename__ = 'lesson_book_paragraphs'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    type = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String)
    position = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)

    lesson_book_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("lesson_books.id", ondelete='CASCADE'),
                                       nullable=False)
