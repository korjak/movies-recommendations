from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import random


app = Flask(__name__)
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="toor",
    database="moviesratings"
)
mycursor = mydb.cursor()


def check_user(username):
    mycursor.execute('SELECT * FROM Users WHERE name="' + username + '"')
    data = mycursor.fetchall()
    if len(data) == 0:
        mycursor.execute('INSERT INTO Users (name)  VALUES ("' + username + '")')


def name_to_id(username):
    mycursor.execute('SELECT userID FROM Users WHERE name="' + username + '"')
    data = mycursor.fetchall()
    return data[0][0]

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        return redirect(url_for('user_home', username=request.form['username']))


@app.route('/user/<username>', methods=['GET', 'POST'])
def user_home(username):
    if request.method == 'GET':
        check_user(username)
        return render_template("user_panel.html", username=username)
    else:
        if request.form['choose_action'] == 'rate':
            return redirect(url_for('give_rates', username=username))
        elif request.form['choose_action'] == 'recommend':
            return 'recommend'
        else:
            return "something went wrong"


@app.route('/user/<username>/rate', methods=['GET', 'POST'])
def give_rates(username):
    if request.method == 'GET':
        mycursor.execute('SELECT * FROM Top_movies T WHERE NOT EXISTS \
                         (SELECT * FROM Rmatrix R WHERE R.movieID=T.movieID AND R.userID=%s) LIMIT 10;', (int(name_to_id(username)),))
        data = mycursor.fetchall()
        return render_template("rates_panel.html", data=data)
    else:
        offset = random.randint(0,4990)
        rates = request.form
        for movie, rate in rates.items():
            mycursor.execute('SELECT * FROM Rmatrix')
            mycursor.execute('INSERT INTO Ratings VALUES (%s, %s, %s)', (int(name_to_id(username)), int(movie), int(rate)))
            mycursor.execute('INSERT INTO Rmatrix VALUES (%s, %s)', (int(name_to_id(username)), int(movie)))
        mycursor.execute('SELECT * FROM Top_movies T WHERE NOT EXISTS \
                                 (SELECT * FROM Rmatrix R WHERE R.movieID=T.movieID AND R.userID=%s) LIMIT 10 OFFSET %s;', (int(name_to_id(username)), offset))
        data = mycursor.fetchall()
        mydb.commit()
        return render_template("rates_panel.html", data=data)


@app.route('/test', methods=['GET', 'POST'])
def tester():
    return render_template("rates_panel.html")



if __name__ == '__main__':
    app.run()
