from pprint import pprint

from requests import get, delete, post

pprint(get('http://localhost:5000/api/lessons').json())  # получение всех уроков

pprint(post('http://localhost:5000/api/lessons',
            json={'title': 'Новый урок', 'description': 'Ещё один новый урок'}).json())  # добавление урока

pprint(get('http://localhost:5000/api/lessons/2').json())  # получение одного урока
pprint(get('http://localhost:5000/api/lessons/999').json())  # получение одного урока (ошибка)

pprint(delete('http://localhost:5000/api/lessons/2').json())  # удаление одного урока
pprint(delete('http://localhost:5000/api/lessons/2').json())  # удаление одного урока (ошибка)
