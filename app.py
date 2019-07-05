from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import random
from numpy import matmul
from numpy.random import randn
from scipy.optimize import fmin
from pandas import DataFrame


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


def cost_function(theta,X,Y):
    J = matmul(theta, X) - Y
    J = J**2
    # TODO: add r(i,j)==1 constraint
    # TODO: establish lambda
    # J = 0.5 * J(where r(i,j)==1) + lambda/2 * sum(theta**2)
    return J

def learn(user_id):
    t0 = randn(1128) # 1128 is a number of tags
    theta = fmin(cost_function,t0,(X,Y))
    # TODO: insert theta vector into DB
    # TODO: where did X and Y come from?
    return theta

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


@app.route('/user/<username>/recommend', methods=['GET'])
def give_recommendations(username):
    prediction = {}
    movies = []
    mycursor.execute('SELECT movieID FROM Top_movies')
    data = mycursor.fetchall()
    df = DataFrame()
    for i in data:
        movies.append(i[0])
    for movie in movies:
        mycursor.execute('SELECT relevance FROM Xs WHERE movieID=' + movie)
        Xtemp = mycursor.fetchall()
        X = []
        for i in Xtemp:
            X.append(i[0])
        df[movie] = X
    mycursor.execute('SELECT * FROM Thetas WHERE userID=' + str(name_to_id(username)))
    data = mycursor.fetchall()
    if len(data) == 0:
        theta = learn(int(name_to_id(username)))
    else:
        theta = []
        for i in data:
            theta.append(i[0])
    for column in df:
        prediction.update({column : matmul(theta,df[column])})
    return str(prediction)



@app.route('/test', methods=['GET', 'POST'])
def tester():
    return render_template("rates_panel.html")



if __name__ == '__main__':
    app.run()
