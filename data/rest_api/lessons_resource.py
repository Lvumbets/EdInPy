from flask import jsonify
from flask_restful import Resource, abort

from data import db_session
from data.rest_api.regparser import lesson_parser
from data.lessons import Lesson


class LessonResource(Resource):
    '''Класс ресурсов для работы с конкретным уроком'''

    def get(self, lesson_id):
        '''Ресурс получения урока по id'''
        abort_if_lesson_not_found(lesson_id)
        db_sess = db_session.create_session()
        lesson = db_sess.query(Lesson).get(lesson_id)
        return jsonify({'lesson': lesson.to_dict(only=('id', 'title', 'description'))})

    def delete(self, lesson_id):
        '''Функция ресурса удаления урока по id'''
        abort_if_lesson_not_found(lesson_id)
        db_sess = db_session.create_session()
        lesson = db_sess.query(Lesson).get(lesson_id)
        db_sess.delete(lesson)
        db_sess.commit()
        return jsonify({'success': 'OK'})


def abort_if_lesson_not_found(lesson_id):
    '''Функция общей работы для "аборта" сайта'''
    session = db_session.create_session()
    lesson = session.query(Lesson).get(lesson_id)
    if not lesson:
        abort(404, message=f"Lesson {lesson_id} not found")


class LessonsListResource(Resource):
    '''Класс ресурсов для работы со всеми уроками'''

    def get(self):
        '''Функция ресурса получения всех уроков'''
        db_sess = db_session.create_session()
        lessons = db_sess.query(Lesson).all()
        return jsonify({'lessons': [lesson.to_dict(only=('id', 'title', 'description')) for lesson in lessons]})

    def post(self):
        '''Функция ресурса для добавления нового урока в список уроков'''
        args = lesson_parser.parse_args()
        db_sess = db_session.create_session()
        lesson = Lesson(
            title=args['title'],
            description=args['description']
        )
        db_sess.add(lesson)
        db_sess.commit()
        return jsonify({'id': lesson.id})
