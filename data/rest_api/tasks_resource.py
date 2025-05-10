from flask import jsonify
from flask_restful import Resource, abort

from data import db_session
from data.rest_api.regparser import task_parser
from data.tasks import Task


class TaskResource(Resource):
    '''Класс ресурсов для работы с конкретной задачей'''

    def get(self, task_id):
        '''Ресурс получения задачи по id'''
        abort_if_task_not_found(task_id)
        db_sess = db_session.create_session()
        task = db_sess.query(Task).get(task_id)
        return jsonify({'task': task.to_dict(only=('id', 'title', 'condition', 'examples', 'less_id'))})

    def delete(self, task_id):
        '''Функция ресурса удаления задачи по id'''
        abort_if_task_not_found(task_id)
        db_sess = db_session.create_session()
        task = db_sess.query(Task).get(task_id)
        db_sess.delete(task)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class TaskListResource(Resource):
    '''Класс ресурсов для работы со всеми задачами'''

    def get(self):
        '''Функция ресурса получения всех задач'''
        db_sess = db_session.create_session()
        tasks = db_sess.query(Task).all()
        return jsonify(
            {'task': [task.to_dict(only=('id', 'title', 'condition', 'examples', 'less_id')) for task in tasks]})

    def post(self):
        '''Функция ресурса для добавления новой задачи в список задач'''
        args = task_parser.parse_args()
        db_sess = db_session.create_session()
        task = Task(
            title=args['title'],
            condition=args['condition'],
            examples=args['examples'],
            less_id=args['less_id']
        )
        db_sess.add(task)
        db_sess.commit()
        return jsonify({'id': task.id})


def abort_if_task_not_found(task_id):
    '''Функция общей работы для "аборта" сайта'''
    session = db_session.create_session()
    task = session.query(Task).get(task_id)
    if not task:
        abort(404, message=f"task {task_id} not found")
