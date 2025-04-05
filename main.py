from flask import Flask, render_template, redirect
from forms.student import RegisterStudent, LoginStudent

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
        return redirect("/") # временно
    return render_template('login_student.html', title='Авторизация ученика', form=form)


def main():
    app.run()


if __name__ == '__main__':
    main()
