from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="toor",
    database="moviesratings"
)
mycursor = mydb.cursor()


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        return redirect(url_for('user_home', username=request.form['username']))


@app.route('/user/<username>', methods=['GET', 'POST'])
def user_home(username):
    mycursor.execute('SELECT * FROM Users WHERE name="' + username + '"')
    data = mycursor.fetchall()
    if request.method == 'GET':
        if len(data) == 0:
            return "no user"
        else:
            return render_template("user_panel.html", username=username)
    else:
        if request.form['choose_action'] == 'rate':
            return 'rate'
        elif request.form['choose_action'] == 'recommend':
            return 'recommend'
        else:
            return "something went wrong"


@app.route('/user/<username>/rate')
def give_rates(username):
    pass


@app.route('/test/<username>', methods=['GET', 'POST'])
def tester(username):
    if request.method == 'GET':
        return render_template("user_panel.html", username=username)
    else:
        if request.form['choose_action'] == 'rate':
            return redirect(url_for('give_rates'), username=username)
        elif request.form['choose_action'] == 'recommend':
            return redirect(url_for('get_recommendations'), username=username)
        else:
            return "something went wrong"


if __name__ == '__main__':
    app.run()
