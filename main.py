from flask import Flask, render_template, redirect, abort, request

from EdInPy.data.learns import Learn
from EdInPy.forms.learn import LearnForm
from forms.student import RegisterStudent, LoginStudent

from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'EDINPY_PROJECT'


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
        # проверка по базе данных и добавление в неё
        # db_sess = db_session.create_session()
        # if db_sess.query(User).filter(User.email == form.email.data).first():
        #    return render_template('register.html', title='Регистрация',
        #                           form=form,
        #                           message="Такой пользователь уже есть")
        # user = User(
        #     name=form.name.data,
        #     email=form.email.data,
        #     surname=form.surname.data,
        #     age=form.age.data,
        #     position=form.position.data,
        #     speciality=form.speciality.data,
        #     address=form.address.data
        # )
        # user.set_password(form.password.data)
        # db_sess.add(user)
        # db_sess.commit()
        return redirect('/login')
    return render_template('register_student.html', title='Регистрация ученика', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginStudent()
    if form.validate_on_submit():
        # Проверка на ученика в бд
        # db_sess = db_session.create_session()
        # user = db_sess.query(User).filter(User.email == form.email.data).first()
        # if user and user.check_password(form.password.data):
        #    login_user(user, remember=form.remember_me.data)
        #    return redirect("/")
        # return render_template('login.html',
        #                       message="Неправильный логин или пароль",
        #                       form=form)
        return redirect("/")  # временно
    return render_template('login_student.html', title='Авторизация ученика', form=form)


@app.route("/learns/<int:learn_id>", methods=['GET', 'POST'])
def show_learn(learn_id):
    '''Страница с уроком'''
    db_sess = db_session.create_session()
    learn = db_sess.query(Learn).filter(Learn.id == learn_id).first()
    if learn:  # если урок найден
        learn_form = LearnForm()  # создание python формы
        examples = [example.split(':') for example in str(learn.examples).split(';')]  # форматирование примеров

        # пока нерабочий обработчик post запроса при нажатии на кнопку "отправить" в уроке
        # if learn_form.validate_on_submit():
        #    return redirect('/')
        return render_template('learn.html', form=learn_form, title='Название урока', learn=learn, examples=examples)
    return abort(404)  # урок не найден


def main():
    db_session.global_init('db/ed_in_py.sqlite')
    app.run()


if __name__ == '__main__':
    main()
