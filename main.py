from flask import Flask, render_template

from data import db_session

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('base.html', title='Шаблон')


def main():
    db_session.global_init('db/ed_in_py.sqlite')
    app.run()


if __name__ == '__main__':
    main()
