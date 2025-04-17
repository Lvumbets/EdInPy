import datetime

from flask import Flask, render_template, redirect, make_response, jsonify
from flask import abort
from flask_login import LoginManager, login_user, login_required, logout_user

from data.lessons import Lesson
from forms.lesson import LessonForm
from data import db_session
from data.students import Student
from forms.student import RegisterStudent, LoginStudent

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = 'EDINPY_PROJECT'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)


@login_manager.user_loader
def load_student(student_id):
    db_sess = db_session.create_session()
    return db_sess.query(Student).get(student_id)


@app.route('/')
def index():
    return render_template('base.html', title='Шаблон')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterStudent()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_student.html', title='Регистрация ученика',
                                   form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Student).filter(Student.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        student = Student(
            name=form.name.data,
            surname=form.surname.data,
            age=form.age.data,
            email=form.email.data
        )
        student.set_password(form.password.data)
        db_sess.add(student)
        db_sess.commit()
        return redirect('/login')
    return render_template('register_student.html', title='Регистрация ученика', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginStudent()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(Student).filter(Student.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/lessons")
        return render_template('login_student.html', form=form, message="Неправильный логин или пароль")
    return render_template('login_student.html', title='Авторизация ученика', form=form)


@app.route("/lessons/<int:lesson_id>", methods=['GET', 'POST'])
def show_lesson(lesson_id):
    '''Страница с уроком'''
    db_sess = db_session.create_session()
    lesson = db_sess.query(Lesson).filter(Lesson.id == lesson_id).first()
    if lesson:  # если урок найден
        lesson_form = LessonForm()  # создание python формы
        examples = [example.split(':') for example in str(lesson.examples).split(';')]  # форматирование примеров

        # пока нерабочий обработчик post запроса при нажатии на кнопку "отправить" в уроке
        if lesson_form.submit.data:
            return redirect('/lessons')
        return render_template('lesson.html', form=lesson_form, title='Название урока', lesson=lesson,
                               examples=examples)
    return abort(404)  # урок не найден


@app.route('/lessons')
def lessons():
    return render_template('lessons.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init('db/ed_in_py.sqlite')
    app.run()


if __name__ == '__main__':
    main()
