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
        return str(request.form)
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


@app.route('/user/<username>/rate', methods=['GET', 'POST'])
def give_rates(username):
    if request.method == 'GET':
        mycursor.execute('SELECT * FROM Top_movies LIMIT 10;')
        data = mycursor.fetchall()
        return render_template("rates_panel.html", data=data)
    else:
        # TODO: each user should have his own rate - OOP?
        rates = {}
        rates.update(request.form)
        return str(rates)


@app.route('/test', methods=['GET', 'POST'])
def tester():
    return render_template("rates_panel.html")


if __name__ == '__main__':
    app.run()
