from pprint import pprint

from requests import get, delete, post


def check_lessons_api():
    pprint(get('http://localhost:5000/api/lessons').json())  # получение всех уроков

    pprint(post('http://localhost:5000/api/lessons', json={'title': 'Новый урок',
                                                           'description': 'Ещё один новый урок'}).json())  # добавление урока

    pprint(get('http://localhost:5000/api/lessons/2').json())  # получение одного урока (по id)
    pprint(get('http://localhost:5000/api/lessons/999').json())  # получение одного урока (ошибка)

    pprint(delete('http://localhost:5000/api/lessons/2').json())  # удаление одного урока
    pprint(delete('http://localhost:5000/api/lessons/2').json())  # удаление одного урока (ошибка)


def check_tasks_api():
    pprint(get('http://localhost:5000/api/tasks').json())  # получение всех задач

    pprint(post('http://localhost:5000/api/tasks', json={'title': 'Следующая задача',
                                                         'condition': 'Опять новая задача',
                                                         'examples': '2,1:1;3,-1:4',
                                                         'less_id': 3}).json())  # добавление задачи

    pprint(get('http://localhost:5000/api/tasks/1').json())  # получение одной задачи (по id)
    pprint(get('http://localhost:5000/api/tasks/-1').json())  # получение одной задачи (по id) (ошибка)

    pprint(delete('http://localhost:5000/api/tasks/5').json())  # удаление одной задачи
    pprint(delete('http://localhost:5000/api/tasks/5').json())  # удаление одного урока (ошибка)


if __name__ == '__main__':
    # сюда вписать функцию(-и) в зависимости от потребности (НЕ ЗАБУДЬТЕ В БД ДЛЯ API ДОБАВИТЬ SerializerMixin)
    check_tasks_api()
