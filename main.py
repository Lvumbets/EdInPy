from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return f'<h1>Hello world!</h1>'




def main():
    app.run()


if __name__ == '__main__':
    main()
