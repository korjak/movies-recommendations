from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import random
from numpy import  transpose
from numpy.random import randn
from scipy.optimize import fmin
from pandas import DataFrame
import operator


app = Flask(__name__)
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="toor",
    database="moviesratings"
)
mycursor = mydb.cursor()
THETAS_NO = 200
ITER_NO = 512000


def check_user(username):
    mycursor.execute('SELECT * FROM Users WHERE name="' + username + '"')
    data = mycursor.fetchall()
    if len(data) == 0:
        mycursor.execute('INSERT INTO Users (name)  VALUES ("' + username + '")')


def name_to_id(username):
    mycursor.execute('SELECT userID FROM Users WHERE name=%s', (username,))
    data = mycursor.fetchall()
    return data[0][0]


def get_param(user_id, X):
    mycursor.execute('SELECT movieID FROM Rmatrix WHERE userID=%s', (user_id,))
    data = mycursor.fetchall()
    movie_list = []
    for i in data:
        movie_list.append(i[0])
    print('X size before dropping: ' + str(X.shape))
    print(X.columns[1])
    print(movie_list)
    for column in X.columns:
        if column not in movie_list:
            X = X.drop(column,1)
    print('X size after dropping: ' + str(X.shape))
    mycursor.execute('SELECT rating FROM Ratings WHERE userID=%s', (user_id,))
    data = mycursor.fetchall()
    Y = []
    for i in data:
        Y.append(i[0])
    return X, Y


def cost_function(theta,X,Y):
    #print("Cost function")
    #print("thetas: " + str(theta.shape))
    #print("X: " + str(X.shape))
    #print("Y: " + str(len(Y)))
    #print("matmul(X,theta): " + str(test.shape))
    J = X @ theta - Y
    J = J**2
    J = sum(J)
    #l = 10
    J = 0.5 * J# + l/2 * sum(theta**2)
    return J


def learn(user_id,X):
    print("Learn")
    t0 = randn(THETAS_NO)     # 1128 is a number of tags
    X, Y = get_param(user_id, X)
    X = transpose(X)
    theta = fmin(cost_function,t0,(X,Y),  maxiter=ITER_NO)
    vmin = cost_function(theta, X, Y)
    #print("******************000000")
    #print(theta[0])
    #print("******************111111")
    #print(theta[1])
    #print("******************222222")
    #print(theta[2])
    #print("******************333333")
    print("vmin: " + str(vmin))
    print(theta)
    for idx, val in enumerate(theta):
        #print('idx: ' + str(idx))
        #print('val: ' + str(val))
        mycursor.execute('INSERT INTO Thetas VALUES (%s, %s, %s)', (user_id, idx+1, val))
    mydb.commit()
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
            return redirect(url_for('give_recommendations', username=username))
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
            mycursor.execute('INSERT INTO Ratings VALUES (%s, %s, %s)', (name_to_id(username), movie, rate))
            mycursor.execute('INSERT INTO Rmatrix VALUES (%s, %s)', (name_to_id(username), movie))
            mydb.commit()
        mycursor.execute('SELECT * FROM Top_movies T WHERE NOT EXISTS \
                                 (SELECT * FROM Rmatrix R WHERE R.movieID=T.movieID AND R.userID=%s) LIMIT 10 OFFSET %s;', (int(name_to_id(username)), offset))
        data = mycursor.fetchall()
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
    movies.remove(187541)   # movie no 187541 seems to be the only one without X values
    for movie in movies:
        mycursor.execute('SELECT relevance FROM Xs WHERE movieID=%s LIMIT %s',(movie, THETAS_NO))
        Xtemp = mycursor.fetchall()
        X = []
        for i in Xtemp:
            X.append(i[0])
        df[movie] = X
    mycursor.execute('SELECT tVal FROM Thetas WHERE userID=%s', (name_to_id(username),))
    data = mycursor.fetchall()
    if len(data) == 0:
        theta = learn(int(name_to_id(username)),df)
        print("Recommendations")
    else:
        theta = []
        for i in data:
            theta.append(i[0])
    for column in df.columns:
        #print('THEEEEEETAAAAAAAA')
        #print(theta)
        prediction.update({column: df[column].dot(theta)})
    prediction_sort = sorted(prediction.items(), key=lambda kv: kv[1], reverse=True)
    movies_names = []
    for key, value in prediction_sort:
        mycursor.execute('SELECT title FROM Movies WHERE movieID=%s', (key,))
        data = mycursor.fetchall()
        movies_names.append(data[0][0])
    return str(movies_names)



@app.route('/test', methods=['GET', 'POST'])
def tester():
    return render_template("rates_panel.html")



if __name__ == '__main__':
    app.run()
