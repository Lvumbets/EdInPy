import datetime
import os
import random
import uuid

from flask import Flask, render_template, redirect, make_response, jsonify, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from data import db_session
from data.lesson_book_paragraphs import LessonBookParagraph, PARAGRAPH_TYPE_IMAGE, PARAGRAPH_TYPE_TEXT
from data.lesson_books import LessonBook
from data.rest_api import lessons_resource, tasks_resource
from data.admins import Admin
from data.lessons import Lesson
from data.solutions import Solution
from data.students import Student
from data.tasks import Task
from data.teachers import Teacher
from forms.admin import LoginAdmin, RegisterAdmin
from forms.lesson import LessonEdit, LessonAdd
from forms.lesson_book import LessonBookAdd, LessonBookEdit
from forms.lesson_book_paragraph import LessonBookParagraphAdd, LessonBookParagraphEdit, LessonBookImageAdd, \
    LessonBookImageEdit
from forms.student import RegisterStudent, LoginStudent
from forms.task import TaskForm, CheckSolve, TaskAdd, TaskEdit
from forms.teacher import RegisterTeacher, LoginTeacher, ChangeStudents
from forms.change_password import Change_Password
from static.config import config

'''Создание ключевых значений и переменных для Flask'''
app = Flask(__name__)
api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'EDINPY_PROJECT'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)
app.config['UPLOAD_FOLDER'] = "static/upload"

'''Глобальные переменные'''
table_now = None  # изменить на None!!!

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


@app.route('/')
def index():
    '''Функция отображения стартовой страницы'''
    return render_template('main_page.html')


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    '''Функция регистрации ученика'''
    form = RegisterStudent()  # форма регистрации

    if form.validate_on_submit():  # если нажали кнопку для сохранения регистрации
        if form.password.data != form.password_again.data:  # проверка на совпадение паролей
            return render_template('register_student.html', form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Student).filter(Student.email == form.email.data).first():  # существует ли уже такой ученик
            return render_template('register_student.html', form=form, message="Такой ученик уже есть")
        # создание нового ученика
        student = Student(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            email=form.email.data
        )
        student.set_password(form.password.data)  # установка хэшированного пароля
        db_sess.add(student)  # добавление нового ученика в бд
        db_sess.commit()  # сохранения изменений в таблице
        db_sess.close()  # конец сессии бд
        return redirect('/login_student')  # перевод на страницу с логином ученика
    return render_template('register_student.html', form=form)  # отображение страницы ученика


@app.route('/login_student', methods=['GET', 'POST'])
def login_student():
    '''Функция логина ученика'''
    global table_now  # глобальная переменная для сессии
    form = LoginStudent()  # форма логина ученика
    if form.validate_on_submit():  # если нажали на кнопку авторизации
        db_sess = db_session.create_session()
        student = db_sess.query(Student).filter(Student.email == form.email.data).first()  # ищем ученика в дб
        if student and student.check_password(form.password.data):  # если логин и пароль совпадают
            table_now = Student  # сессию на сайте для пользователя из таблицы учеников
            login_user(student, remember=form.remember_me.data)  # авторизация ученика
            return redirect("/lessons")  # перейти в список уроков
        return render_template('login_student.html', form=form,
                               message="Неправильный логин или пароль")  # если логин или пароль не те
    return render_template('login_student.html', form=form)  # отображение страницы логина


@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    '''Функция регистрации учителя'''
    form = RegisterTeacher()  # форма регистрации учителя
    if form.validate_on_submit():  # если нажата кнопка регистрации
        if form.password.data != form.password_again.data:  # если введённые пароли не совпадают
            return render_template('register_teacher.html', form=form,
                                   message="Пароли не совпадают")  # отображение ошибки
        if form.access_code.data not in config.teachers_access_tokens:
            config.update_teachers_passwords()
            return render_template('register_teacher.html', form=form,
                                   message="Неверный код учителя")  # отображение ошибки
        config.update_teachers_passwords()
        db_sess = db_session.create_session()
        if db_sess.query(Teacher).filter(Teacher.email == form.email.data).first():  # если такой учитель уже есть
            return render_template('register_teacher.html', form=form,
                                   message="Такой учитель уже есть")  # отображение ошибки
        # создание учителя для дб
        teacher = Teacher(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            email=form.email.data,
            students=form.students.data
        )
        teacher.set_password(form.password.data)  # установка пароля для учителя
        db_sess.add(teacher)  # добавление учителя в бд

        '''Добавление id учителя к карточкам выбранных учеников'''
        try:
            if len(form.students.data.split()):
                for id in form.students.data.split():
                    student = db_sess.query(Student).filter(Student.id == id).first()
                    if student:
                        student.teacher_id = teacher.id
        except Exception:
            return render_template('register_teacher.html', form=form, message='Данные об учениках введены неверно')

        db_sess.commit()  # сохранение изменений в бд
        db_sess.close()
        return redirect('/login_teacher')  # перевод на авторизацию учителя
    return render_template('register_teacher.html', form=form)  # отображение страницы регистрации учителя


@app.route('/login_teacher', methods=['GET', 'POST'])
def login_teacher():
    '''Функция логина учителя'''
    global table_now  # переменная с таблицей, из которой надо авторизовать пользователя в сессии
    form = LoginTeacher()  # форма логина учителя
    if form.validate_on_submit():  # при нажатии на кнопку
        db_sess = db_session.create_session()
        teacher = db_sess.query(Teacher).filter(Teacher.email == form.email.data).first()  # поиск учителя по бд
        if teacher and teacher.check_password(form.password.data):  # если учитель найден - логинимся
            table_now = Teacher  # выбор таблицы учителей для сессии
            login_user(teacher, remember=form.remember_me.data)  # логин учителя
            db_sess.close()
            return redirect("/lessons")  # переходим на страницу уроков
        db_sess.close()
        return render_template('login_teacher.html', form=form,
                               message="Неправильный логин или пароль")  # отображение ошибки
    return render_template('login_teacher.html', form=form)  # отображение страницы логина учителя


@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    '''Функция регистрации админа'''
    form = RegisterAdmin()  # форма регистрации админа
    if form.validate_on_submit():  # если нажата кнопка регистрации
        if form.password.data != form.password_again.data:  # если введённые пароли не совпадают
            return render_template('register_admin.html', form=form,
                                   message="Пароли не совпадают")  # отображение ошибки
        if form.access_code.data not in config.admins_access_tokens:
            config.update_admins_passwords()
            return render_template('register_admin.html', form=form,
                                   message="Неверный код администратора")  # отображение ошибки
        config.update_admins_passwords()
        db_sess = db_session.create_session()
        if db_sess.query(Admin).filter(Admin.email == form.email.data).first():  # если такой админ уже есть
            return render_template('register_admin.html', form=form,
                                   message="Такой администратор уже есть")  # отображение ошибки
        # создание админа для дб
        admin = Admin(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            email=form.email.data,
            access_level=1,
        )
        admin.set_password(form.password.data)  # установка пароля для админа
        db_sess.add(admin)  # добавление админа в бд
        db_sess.commit()  # сохранение изменений в бд
        db_sess.close()
        return redirect('/login_admin')  # перевод на авторизацию админа
    return render_template('register_admin.html', form=form)  # отображение страницы регистрации админа


@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    '''Функция логина администратора'''
    global table_now  # переменная с таблицей, из которой надо авторизовать пользователя в сессии
    form = LoginAdmin()  # форма логина админа
    if form.validate_on_submit():  # при нажатии на кнопку
        db_sess = db_session.create_session()
        admin = db_sess.query(Admin).filter(Admin.email == form.email.data).first()  # поиск админа по бд
        if admin and admin.check_password(form.password.data):  # если админ найден - логинимся
            table_now = Admin
            login_user(admin, remember=form.remember_me.data)  # логин админа в сессии
            db_sess.close()
            return redirect("/lessons")  # переходим на страницу уроков
        db_sess.close()
        return render_template('login_admin.html', form=form,
                               message="Неправильный логин или пароль")  # отображение ошибки
    return render_template('login_admin.html', form=form)  # отображении страницы логина админа


@app.route('/lessons')
def lessons():
    '''Функция отображения уроков'''
    db_sess = db_session.create_session()
    less = db_sess.query(Lesson).all()  # получение всех уроков
    is_admin = table_now == Admin
    db_sess.close()
    return render_template('lessons.html', lessons=less, is_admin=is_admin)  # отображение страницы уроков


@app.route("/lessons/<int:lesson_id>/tasks")
def show_lesson(lesson_id):
    '''Функция отображения урока и его задача'''
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson_id).first()  # получение урока
    tasks = db_sess.query(Task).filter(Task.less_id == lesson_id)  # получение задач
    is_admin = table_now == Admin
    db_sess.close()
    return render_template(f'lesson.html', lesson=lesson, tasks=tasks,
                           is_admin=is_admin)  # отображение урока и его задач


@app.route('/lessons/add', methods=['GET', 'POST'])
def add_lesson():
    '''Функция страницы добавления нового урока'''
    lesson_add = LessonAdd()
    db_sess = db_session.create_session()

    if lesson_add.submit.data:  # если нажата кнопка 'добавить'
        lesson = Lesson(
            title=lesson_add.title.data,
            description=lesson_add.description.data,
        )
        db_sess.add(lesson)
        db_sess.commit()
        db_sess.close()
        return redirect('/lessons')
    db_sess.close()
    return render_template('add_lesson.html', form=lesson_add)


@app.route('/lessons/edit/<int:lesson_id>', methods=['GET', 'POST'])
def edit_lesson(lesson_id):
    '''Функция страницы редактирования урока'''
    lesson_edit = LessonEdit()
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson_id).first()

    if lesson_edit.submit.data:  # если нажали на кнопку 'сохранить'
        lesson.title = lesson_edit.title.data
        lesson.description = lesson_edit.description.data
        db_sess.commit()
        db_sess.close()
        return redirect('/lessons')

    # отображать данные этого урока в форме изначально (для их изменения)
    lesson_edit.title.data = lesson.title
    lesson_edit.description.data = lesson.description
    db_sess.close()
    return render_template('edit_lesson.html', form=lesson_edit)


@app.route('/lessons/delete/<int:lesson_id>')
def delete_lesson(lesson_id):
    '''Функция удаления урока'''
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson_id).first()
    db_sess.delete(lesson)
    db_sess.commit()
    db_sess.close()
    return redirect('/lessons')


@app.route("/books/<int:book_id>")
def show_book(book_id):
    """Функция отображения выбранного учебника"""
    with db_session.create_session() as dbs:
        book = dbs.query(LessonBook).filter(LessonBook.id == book_id).first()
        book.paragraphs.sort(key=lambda x: x.position)  # для подгрузки разделов
        if not book:
            return redirect('/lessons')

        is_admin = current_user.__class__ == Admin
        return render_template(f'lesson_book.html', book=book, is_admin=is_admin,
                               PARAGRAPH_TYPE_IMAGE=PARAGRAPH_TYPE_IMAGE, PARAGRAPH_TYPE_TEXT=PARAGRAPH_TYPE_TEXT)


@app.route('/lessons/<int:lesson_id>/books/add', methods=['GET', 'POST'])
@login_required
def add_lesson_book(lesson_id):
    """Функция страницы добавления нового учебника"""
    if current_user.__class__ != Admin:
        return redirect(f'/lessons/{lesson_id}/tasks')
    form = LessonBookAdd()  # форма добавления учебника
    if form.validate_on_submit():  # если нажата кнопка submit
        with db_session.create_session() as dbs:
            book = LessonBook(
                title=form.title.data,
                description=form.description.data,
                lesson_id=lesson_id
            )
            dbs.add(book)
            dbs.commit()
            return redirect(f'/lessons/{lesson_id}/tasks')
    return render_template('add_lesson_book.html', form=form)


@app.route('/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_lesson_book(book_id):
    '''Функция страницы редактирования учебника'''
    if current_user.__class__ != Admin:
        return redirect(f'/lessons')
    form = LessonBookEdit()
    with db_session.create_session() as dbs:
        book = dbs.query(LessonBook).filter(LessonBook.id == book_id).first()
        book.paragraphs.sort(key=lambda x: x.position)  # для подгрузки разделов

        if not book:
            return redirect(f'/lessons')
        if form.validate_on_submit():  # если нажата кнопка submit
            book.title = form.title.data
            book.description = form.description.data
            dbs.commit()
            return redirect(f'/lessons/{book.lesson_id}/tasks')

        # отображать данные в форме изначально (для их изменения)
        form.title.data = book.title
        form.description.data = book.description

    return render_template('edit_lesson_book.html', form=form, book=book, PARAGRAPH_TYPE_IMAGE=PARAGRAPH_TYPE_IMAGE,
                           PARAGRAPH_TYPE_TEXT=PARAGRAPH_TYPE_TEXT)


@app.route('/books/delete/<int:book_id>')
@login_required
def delete_lesson_book(book_id):
    """Функция удаления учебника"""
    if current_user.__class__ != Admin:
        return redirect(f'/lessons')
    with db_session.create_session() as dbs:
        book = dbs.query(LessonBook).filter(LessonBook.id == book_id).first()
        if not book:
            return redirect(f'/lessons')
        dbs.delete(book)
        dbs.commit()
    return redirect(f'/lessons/{book.lesson_id}/tasks')


@app.route('/books/<int:book_id>/book_paragraphs/add', methods=['GET', 'POST'])
@login_required
def add_book_paragraph(book_id):
    """Функция страницы добавления раздела учебника"""
    if current_user.__class__ != Admin:
        return redirect(f'/books/{book_id}')
    form = LessonBookParagraphAdd()  # форма добавления раздела учебника
    if form.validate_on_submit():  # если нажата кнопка submit
        with db_session.create_session() as dbs:
            paragraph = LessonBookParagraph(
                type=PARAGRAPH_TYPE_TEXT,
                content=form.content.data,
                position=form.position.data,
                lesson_book_id=book_id
            )
            dbs.add(paragraph)
            dbs.commit()
            return redirect(f'/books/edit/{book_id}')
    return render_template('add_book_paragraph.html', form=form)


@app.route('/book_paragraphs/edit/<int:paragraph_id>', methods=['GET', 'POST'])
@login_required
def edit_book_paragraph(paragraph_id):
    '''Функция страницы редактирования раздела учебника'''
    if current_user.__class__ != Admin:
        return redirect(f'/lessons')
    form = LessonBookParagraphEdit()
    with db_session.create_session() as dbs:
        paragraph = dbs.query(LessonBookParagraph).filter(LessonBookParagraph.id == paragraph_id).first()

        if not paragraph:
            return redirect(f'/lessons')
        if form.validate_on_submit():  # если нажата кнопка submit
            paragraph.content = form.content.data
            paragraph.position = form.position.data
            dbs.commit()
            return redirect(f'/books/edit/{paragraph.lesson_book_id}')

        # отображать данные в форме изначально (для их изменения)
        form.content.data = paragraph.content
        form.position.data = paragraph.position

    return render_template('edit_book_paragraph.html', form=form)


@app.route('/books/<int:book_id>/book_paragraphs/add_image', methods=['GET', 'POST'])
@login_required
def add_book_paragraph_image(book_id):
    """Функция страницы добавления изображения учебника"""
    if current_user.__class__ != Admin:
        return redirect(f'/books/{book_id}')
    form = LessonBookImageAdd()  # форма добавления изображения
    if form.validate_on_submit():  # если нажата кнопка submit
        ext = form.image.data.filename.rsplit('.', 1)[1].lower()
        filename = f'{str(uuid.uuid4())}.{ext}'
        with db_session.create_session() as dbs:
            paragraph = LessonBookParagraph(
                type=PARAGRAPH_TYPE_IMAGE,
                content=filename,
                position=form.position.data,
                lesson_book_id=book_id
            )
            dbs.add(paragraph)
            dbs.commit()
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))
            return redirect(f'/books/edit/{book_id}')
    return render_template('add_book_image.html', form=form)


@app.route('/book_paragraphs/edit_image/<int:paragraph_id>', methods=['GET', 'POST'])
@login_required
def edit_book_paragraph_image(paragraph_id):
    '''Функция страницы редактирования раздела учебника'''
    if current_user.__class__ != Admin:
        return redirect(f'/lessons')
    form = LessonBookImageEdit()
    with db_session.create_session() as dbs:
        paragraph = dbs.query(LessonBookParagraph).filter(LessonBookParagraph.id == paragraph_id).first()

        if not paragraph:
            return redirect(f'/lessons')
        if form.validate_on_submit():  # если нажата кнопка submit
            paragraph.position = form.position.data
            dbs.commit()
            return redirect(f'/books/edit/{paragraph.lesson_book_id}')

        # отображать данные в форме изначально (для их изменения)
        form.position.data = paragraph.position

    return render_template('edit_book_image.html', form=form)


@app.route('/book_paragraphs/delete/<int:paragraph_id>')
@login_required
def delete_book_paragraph(paragraph_id):
    """Функция удаления раздела/изображения учебника"""
    if current_user.__class__ != Admin:
        return redirect(f'/lessons')
    with db_session.create_session() as dbs:
        paragraph = dbs.query(LessonBookParagraph).filter(LessonBookParagraph.id == paragraph_id).first()
        if not paragraph:
            return redirect(f'/lessons')
        dbs.delete(paragraph)
        dbs.commit()
    return redirect(f'/books/edit/{paragraph.lesson_book_id}')


@app.route("/lessons/<int:lesson_id>/tasks/<int:task_id>", methods=['GET', 'POST'])
def show_task(lesson_id, task_id):
    '''Функция отображения выбранного урока'''
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == task_id).first()  # получение урока из дб
    if task:  # если урок найден
        if not table_now:  # если пользователь зашёл на задачу, но не зарегистрирован => переводим на регистрацию
            return redirect('/register_student')

        task_form = TaskForm()
        try:
            examples = [example.split(':') for example in str(task.examples).split(';')]  # форматирование примеров
        except Exception:  # если неправильно введены примеры
            task.title = 'Задача в разработке!'
            db_sess.commit()
            return redirect(f'/lessons/{lesson_id}/tasks')

        old_solution = db_sess.query(Solution).filter(current_user.id == Solution.student_id,
                                                      Solution.task_id == task.id).first()  # ищем старое решение

        if task_form.submit.data and table_now == Student:  # если отправил код ученик
            def add_new_solution():
                '''Функция добавления нового решения'''
                solution = Solution(
                    answer=task_form.code.data,
                    student_id=db_sess.query(Student).filter(current_user.id == Student.id).first().id,
                    task_id=task.id
                )
                db_sess.add(solution)
                db_sess.commit()
                db_sess.close()

            # если есть старое решение и оно неправильное => заменить на новое
            if old_solution:  # если есть старое решение
                if not old_solution.is_solved:  # если оно неверное => удаляем старое и пропускаем новое решение
                    db_sess.delete(old_solution)
                    add_new_solution()
                    return redirect(f'/lessons/{lesson_id}/tasks')
            else:  # если отправляем решение в первый раз
                add_new_solution()
                return redirect(f'/lessons/{lesson_id}/tasks')
            db_sess.close()
            return render_template(f'task.html', form=task_form, task=task, examples=examples,
                                   is_checked=old_solution.is_checked, is_solved=old_solution.is_solved,
                                   is_send=True)

        is_checked, is_solved = False, False
        if old_solution:  # если решение было отправлено раньше
            is_send = True
            if old_solution.is_checked:  # если решение было проверено
                is_checked = True
            else:  # если решение не было проверено
                is_checked = False
            if old_solution.is_solved:  # если решение было верным
                is_solved = True
            else:  # если решение не было верным
                is_solved = False
        else:  # если ещё не отправляли
            is_send = False
        if table_now in [Teacher, Admin]:
            is_send = False
        try:
            return render_template(f'task.html', form=task_form, task=task, examples=examples,
                                   is_checked=is_checked, is_solved=is_solved, is_send=is_send)  # отображаем задачу
        except Exception:
            task.title = 'Задача в разработке!'
            db_sess.commit()
            return redirect(f'/lessons/{lesson_id}/tasks')

    db_sess.close()
    return abort(404)  # задача не найдена


@app.route('/lessons/<int:lesson_id>/tasks/add', methods=['GET', 'POST'])
def add_task(lesson_id):
    '''Функция страницы добавления новой задачи'''
    task_add = TaskAdd()
    db_sess = db_session.create_session()

    if task_add.submit.data:  # если нажата кнопка 'добавить'
        task = Task(
            title=task_add.title.data,
            condition=task_add.condition.data,
            examples=task_add.examples.data,
            less_id=lesson_id
        )
        db_sess.add(task)
        db_sess.commit()
        db_sess.close()
        return redirect(f'/lessons/{lesson_id}/tasks')
    db_sess.close()
    return render_template('add_task.html', form=task_add)


@app.route('/lessons/<int:lesson_id>/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(lesson_id, task_id):
    '''Функция страницы редактирования урока'''
    task_edit = TaskEdit()
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == task_id).first()
    lessons_id = [lesson.id for lesson in db_sess.query(Task).all()]

    if task_edit.submit.data:  # если нажали на кнопку 'сохранить'
        if task_edit.less_id.data not in lessons_id:  # если написан номер несуществующего урока
            return render_template('edit_task.html', form=task_edit, message='Такого урока не существует')
        task.title = task_edit.title.data
        task.condition = task_edit.condition.data
        task.examples = task_edit.examples.data
        task.less_id = task_edit.less_id.data
        db_sess.commit()
        db_sess.close()
        return redirect(f'/lessons/{lesson_id}/tasks')

    # отображать данные этой задачи в форме изначально (для их изменения)
    task_edit.title.data = task.title
    task_edit.condition.data = task.condition
    task_edit.examples.data = task.examples
    task_edit.less_id.data = task.less_id
    db_sess.close()
    return render_template('edit_task.html', form=task_edit)


@app.route('/lessons/<int:lesson_id>/tasks/delete/<int:task_id>')
def delete_task(lesson_id, task_id):
    '''Функция удаления задачи'''
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == task_id).first()
    db_sess.delete(task)
    db_sess.commit()
    db_sess.close()
    return redirect(f'/lessons/{lesson_id}/tasks')


@app.route('/check_solutions')
def show_solutions():
    '''Функция отображения решений учеников'''
    if table_now == Teacher:
        db_sess = db_session.create_session()
        solutions = db_sess.query(Solution).filter(Solution.is_checked == False)
        lst = []
        for solution in solutions:
            student = db_sess.query(Student).filter(Student.id == solution.student_id).first()
            task = db_sess.query(Task).filter(Task.id == solution.task_id).first()
            lst.append(((student.name, student.surname), task.title, str(solution.student_id), solution.id))
        db_sess.close()
        return render_template('check_solutions.html', solutions=lst)
    return redirect('/')


@app.route('/check_solutions/<int:solution_id>', methods=['GET', 'POST'])
def show_solution(solution_id):
    db_sess = db_session.create_session()
    solution = db_sess.query(Solution).filter(Solution.id == solution_id).first()
    student = db_sess.query(Student).filter(Student.id == solution.student_id).first()
    task = db_sess.query(Task).filter(Task.id == solution.task_id).first()
    examples = [example.split(':') for example in str(task.examples).split(';')]

    form = CheckSolve()
    if form.submit.data:  # если нажата кнопка 'сохранить'
        if form.is_solved.data:  # если задача решена
            student.completed_tasks += 1  # к кол-ву решённых задач
            solution.is_checked = True  # проверена
            solution.is_solved = True  # решена
        else:  # если не решена
            solution.is_checked = True  # проверена
            solution.is_solved = False  # не решена
        db_sess.commit()
        db_sess.close()
        return redirect('/check_solutions')
    db_sess.close()
    return render_template('check_solution.html', solution=solution, student=student, task=task, examples=examples,
                           form=form)


@app.route('/about_us')
def about_us():
    '''Функция для отображения страницы "о нас"'''
    return render_template('about_us.html')


@login_manager.user_loader
def load_user(id):
    '''Функция авторизации пользователя в сессии'''
    db_sess = db_session.create_session()
    if table_now:
        return Session.get(entity=table_now, ident=id, self=db_sess)  # создание сессии


class Page:
    def __init__(self, link, name=None, enabled=True):
        self.name = name
        self.link = link
        self.enabled = enabled


@app.route('/rating')
def rating():
    '''Функция страницы рейтинга'''
    return render_template('rating.html')
    page_arg = request.args.get('page')
    if not page_arg:
        page_arg = 0
    else:
        page_arg = int(page_arg) - 1
    page_limit = 20
    with db_session.create_session() as dbs:
        cnt = dbs.query(Student).count()
        if page_arg * page_limit >= cnt:
            return redirect('rating')
        users = dbs.query(Student).order_by(Student.completed_tasks.desc(), Student.surname.asc(),
                                            Student.name.asc()).limit(page_limit).offset(page_arg * page_limit)
        pages = []
        for i in range(page_arg - 2, page_arg + 3):
            if i >= 0 and i * page_limit < cnt:
                page = Page(f"/rating?page={i + 1}", i + 1)
                if i == page_arg:
                    page.enabled = False
                pages.append(page)
        prev_page = Page(f"/rating?page={page_arg}")
        next_page = Page(f"/rating?page={page_arg + 2}")
        if page_arg - 1 < 0:
            prev_page.enabled = False
        if (page_arg + 1) * page_limit >= cnt:
            next_page.enabled = False
        return render_template('rating.html', users=users, pages=pages, prev_page=prev_page, next_page=next_page)


@app.route('/profile')
def profile():
    is_teacher = table_now == Teacher
    if is_teacher:  # если авторизован учитель => получаем id его учеников и находим их
        db_sess = db_session.create_session()
        students = db_sess.query(Student).filter(Student.id.in_(str(current_user.students).split()))
        lst = [db_sess.query(Student).filter(Student.id == student.id).first() for student in students]
        db_sess.close()
        return render_template('profile.html', user=current_user, is_teacher=is_teacher, lst=lst)
    return render_template('profile.html', user=current_user, is_teacher=is_teacher)


@app.route('/load_image', methods=['POST', 'GET'])
@login_required
def load_image():
    '''Функция загрузки изображений'''
    if request.method == 'POST':
        file = request.files['file']
        if file.filename:
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f'{str(uuid.uuid4())}.{ext}'
            with db_session.create_session() as dbs:
                user = dbs.query(table_now).filter(current_user.id == table_now.id).first()
                user.image_name = filename
                dbs.commit()
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))
                return redirect('/profile')
    return render_template('load_image.html')


@app.route('/change_students', methods=['POST', 'GET'])
def change_students():
    '''Функция изменения учеников учителя'''
    form = ChangeStudents()
    db_sess = db_session.create_session()
    teacher = db_sess.query(Teacher).filter(Teacher.id == current_user.id).first()

    if form.submit.data:  # если нажата кнопка 'сохранить'
        teacher.students = form.students.data

        """Привязывание учеников к учителю"""
        try:
            if len(teacher.students.split()):
                for student_id in teacher.students.split():
                    student = db_sess.query(Student).filter(Student.id == student_id).first()
                    if student:
                        student.teacher_id = teacher.id
        except Exception:
            return render_template('change_students.html', form=form, message='Данные введены неверно')

        db_sess.commit()
        db_sess.close()
        return redirect('/profile')

    form.students.data = teacher.students
    db_sess.close()
    return render_template('change_students.html', form=form)


@app.route('/change_password', methods=['POST', 'GET'])
@login_required
def change_password():
    '''Функция изменения пароля'''
    form = Change_Password()  # форма изменения пароля
    if form.validate_on_submit():  # если нажата кнопка изменения
        if form.new_password.data != form.new_password_again.data:  # если введённые пароли не совпадают
            return render_template('change_password.html', form=form,
                                   message="Пароли не совпадают")  # отображение ошибки
        if not current_user.check_password(form.current_password.data):
            return render_template('change_password.html', form=form,
                                   message="Неверно введён текущий пароль")  # отображение ошибки
        if form.current_password.data == form.new_password.data:
            return render_template('change_password.html', form=form,
                                   message="Новый и Текущий пароль совпадают")  # отображение ошибки
        with db_session.create_session() as dbs:
            user = dbs.query(current_user.__class__).filter(current_user.id == table_now.id).first()
            user.set_password(form.new_password.data)
            dbs.commit()
        return redirect('/profile')  # перевод на профиль
    return render_template('change_password.html', form=form)


def remove_unused_uploaded_files():
    """Функция удаления неиспользуемых загруженных файлов"""
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    uploaded_files = set([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])

    used_images = set()
    with db_session.create_session() as db_sess:
        for cl in (Admin, Student, Teacher):
            for i in db_sess.query(cl):
                if i.image_name:
                    used_images.add(i.image_name)
        for i in db_sess.query(LessonBookParagraph).filter(LessonBookParagraph.type == PARAGRAPH_TYPE_IMAGE):
            if i.content:
                used_images.add(i.content)

    print("Going to remove unused uploaded files:")

    for i in uploaded_files - used_images:
        file_path = os.path.join(path, i)
        print("Removing", file_path)
        os.remove(file_path)


@login_manager.user_loader
def load_user(id):
    '''Функция авторизации пользователя в сессии'''
    db_sess = db_session.create_session()
    if table_now:
        return Session.get(entity=table_now, ident=id, self=db_sess)  # создание сессии


@app.route('/logout')
@login_required
def logout():
    '''Функция деавторизации пользователя'''
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    '''Функция выброса ошибки о ненайденной странице'''
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    '''Функция выброса ошибки о неправильном request запросе'''
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    '''Функция запуска сайта'''
    api.add_resource(lessons_resource.LessonsListResource, '/api/lessons')  # api для списка уроков
    api.add_resource(lessons_resource.LessonResource, '/api/lessons/<int:lesson_id>')  # api для конкретного урока

    api.add_resource(tasks_resource.TaskListResource, '/api/tasks')  # api для списка задач
    api.add_resource(tasks_resource.TaskResource, '/api/tasks/<int:task_id>')  # api для конкретной задачи

    config.update_teachers_passwords()  # получение новых кодов для учителей
    config.update_admins_passwords()  # получение новых кодов для админов

    db_session.global_init('db/ed_in_py.sqlite')  # инициализация базы данных

    remove_unused_uploaded_files()

    app.run()


if __name__ == '__main__':
    '''Если был запущен этот файл'''
    main()
