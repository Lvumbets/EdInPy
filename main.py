import datetime
import os
import uuid

from flask import Flask, render_template, redirect, make_response, jsonify, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from data import db_session
from data.admins import Admin
from data.lessons import Lesson
from data.solutions import Solution
from data.students import Student
from data.tasks import Task
from data.teachers import Teacher
from forms.admin import LoginAdmin, RegisterAdmin
from forms.lesson import LessonEdit, LessonAdd
from forms.student import RegisterStudent, LoginStudent
from forms.task import TaskForm, CheckSolve
from forms.teacher import RegisterTeacher, LoginTeacher
from static.config import config

'''Создание ключевых значений и переменных для Flask'''
app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'EDINPY_PROJECT'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)
app.config['UPLOAD_FOLDER'] = "static/upload"

'''Глобальные переменные'''
table_now = Admin  # изменить на None!!!

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


@app.route('/')
def index():
    '''Функция отображения стартовой страницы'''
    return render_template('base.html')


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
        if len(form.students.data.split()):
            for id in form.students.data.split():
                student = db_sess.query(Student).filter(Student.id == id).first()
                if student:
                    student.teacher_id = teacher.id

        db_sess.commit()  # сохранение изменений в бд
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
            return redirect("/lessons")  # переходим на страницу уроков
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
            return redirect("/lessons")  # переходим на страницу уроков
        return render_template('login_admin.html', form=form,
                               message="Неправильный логин или пароль")  # отображение ошибки
    return render_template('login_admin.html', form=form)  # отображении страницы логина админа


@app.route('/about_us')
def about_us():
    '''Функция для отображения страницы "о нас"'''
    return render_template('about_us.html')


@app.route('/lessons')
def lessons():
    '''Функция отображения уроков'''
    db_sess = db_session.create_session()
    less = db_sess.query(Lesson).all()  # получение всех уроков
    return render_template('lessons.html', lessons=less, table_now=table_now,
                           Admin=Admin)  # отображение страницы уроков


@app.route("/lessons/<int:lesson_id>")
def show_lesson(lesson_id):
    '''Функция отображения урока и его задача'''
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson_id).first()  # получение урока
    tasks = db_sess.query(Task).filter(Task.less_id == lesson_id)  # получение задач
    return render_template(f'lesson.html', lesson=lesson, tasks=tasks)  # отображение урока и его задач


@app.route("/lessons/<int:lesson_id>/tasks/<int:task_id>", methods=['GET', 'POST'])
def show_task(lesson_id, task_id):
    '''Функция отображения выбранного урока'''
    db_sess = db_session.create_session()
    task = db_sess.query(Task).filter(Task.id == task_id).first()  # получение урока из дб
    if task:  # если урок найден
        task_form = TaskForm()  # создание python формы
        examples = [example.split(':') for example in str(task.examples).split(';')]  # форматирование примеров задачи
        old_solution = db_sess.query(Solution).filter(current_user.id == Solution.student_id,
                                                      Solution.task_id == task.id).first()  # ищем старое решение
        # пока нерабочий обработчик post запроса при нажатии на кнопку "отправить" в задаче
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

            # если есть старое решение и оно неправильное => заменить на новое
            if old_solution:  # если есть старое решение
                if not old_solution.is_solved:  # если оно неверное => удаляем старое и пропускаем новое решение
                    db_sess.delete(old_solution)
                    add_new_solution()
                    return redirect(f'/lessons/{lesson_id}')
            else:  # если отправляем решение в первый раз
                add_new_solution()
                return redirect(f'/lessons/{lesson_id}')
            return render_template(f'task.html', form=task_form, task=task, examples=examples,
                                   is_checked=old_solution.is_checked, is_solved=old_solution.is_solved, is_send=True)

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

        return render_template(f'task.html', form=task_form, task=task, examples=examples,
                               is_checked=is_checked, is_solved=is_solved, is_send=is_send)
    return abort(404)  # урок не найден


@app.route('/check_solutions')
def show_solutions():
    if table_now == Teacher:
        db_sess = db_session.create_session()
        solutions = db_sess.query(Solution).filter(Solution.is_checked == False)
        lst = []
        for solution in solutions:
            student = db_sess.query(Student).filter(Student.id == solution.student_id).first()
            task = db_sess.query(Task).filter(Task.id == solution.task_id).first()
            lst.append(((student.name, student.surname), task.title, solution.id))
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
        return redirect('/check_solutions')
    return render_template('check_solution.html', solution=solution, student=student, task=task, examples=examples,
                           form=form)


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
        return redirect('/lessons')

    # отображать данные этого урока в форме изначально (для их изменения)
    lesson_edit.title.data = lesson.title
    lesson_edit.description.data = lesson.description
    return render_template('edit_lesson.html', form=lesson_edit)


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
        return redirect('/lessons')
    return render_template('add_lesson.html', form=lesson_add)


@app.route('/lessons/delete/<int:lesson_id>')
def delete_lesson(lesson_id):
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson_id).first()
    db_sess.delete(lesson)
    db_sess.commit()
    return redirect('/lessons')


@login_manager.user_loader
def load_user(id):
    '''Функция авторизации пользователя в сессии'''
    db_sess = db_session.create_session()
    if table_now:
        return Session.get(entity=table_now, ident=id, self=db_sess)  # создание сессии


@app.route('/rating')
def rating():
    return render_template('rating.html')


@app.route('/logout')
@login_required
def logout():
    '''Функция деавторизации пользователя'''
    logout_user()
    return redirect("/")


@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)


@login_required
@app.route('/load_image', methods=['POST', 'GET'])
def load_image():
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
    return render_template('load_image.html')


@app.errorhandler(404)
def not_found(error):
    '''Функция выброса ошибки о ненайденной странице'''
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    '''функция выброса ошибки о неправильном request запросе'''
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    '''Функция запуска сайта'''
    config.update_teachers_passwords()  # получение новых кодов для учителей
    config.update_admins_passwords()  # получение новых кодов для админов
    db_session.global_init('db/ed_in_py.sqlite')
    app.run()


if __name__ == '__main__':
    '''Если был запущен этот файл'''
    main()
