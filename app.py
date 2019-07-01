from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        return user_home()

@app.route('/user/<username>')
def user_home():
    pass


if __name__ == '__main__':
    app.run()