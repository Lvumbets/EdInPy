import random
import string

teachers_access_tokens = []
admins_access_tokens = []


def generate_password(start, end):
    """Функция генератора кода"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(random.randint(start, end)))
    return password


def update_teachers_passwords():
    """Функция создания 10 кодов для учителей"""
    teachers_access_tokens.clear()
    for _ in range(10):
        teachers_access_tokens.append(generate_password(5, 10))
    print(f'Коды для учителей: {teachers_access_tokens}')


def update_admins_passwords():
    """Функция создания 10 кодов для администраторов"""
    admins_access_tokens.clear()
    for _ in range(10):
        admins_access_tokens.append(generate_password(10, 20))
    print(f'Коды для админов: {admins_access_tokens}')
