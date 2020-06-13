from flask import *

from werkzeug.security import generate_password_hash,check_password_hash

import pymysql

import os

try:
    host="localhost";user="root";dbname="QandA"
    conn = pymysql.connect(host, user=user,port=3306,passwd="", db=dbname)
    cursor=conn.cursor()
except Exception as e:
	print(e)

app = Flask(__name__)
app.config['SECRET_KEY']=os.urandom(24)

def get_current_user():
    user_result=None
    if 'user' in session:
        user=session['user']
        print("The User is ",user)
        host="localhost";user1="root";dbname="QandA"
        conn = pymysql.connect(host, user=user1,port=3306,passwd="", db=dbname)
        cursor=conn.cursor()
        cursor.execute("SELECT id,name,password from users where name=%s",(user))
        user_result=cursor.fetchall()
        print("user cursor",user_result)
    return user_result
@app.route('/')
def index():

    user = get_current_user()
    if user != None:
        user=user[0][1]
    else:
        user=None
    print(user)
    return render_template('home.html',user=user)

@app.route('/register',methods=['GET','POST'])
def register():
    user = get_current_user()
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        hashed_password=generate_password_hash(password,method="sha256")
        host="localhost";user="root";dbname="QandA"
        conn = pymysql.connect(host, user=user,port=3306,passwd="", db=dbname)
        cursor=conn.cursor()
        cursor.execute("INSERT into users(name,password,expert,admin) values (%s,%s,%s,%s)",(name,hashed_password,0,0))
        conn.commit()
        conn.close()
        return "<h1>User Created</h1>"
    return render_template('register.html')

@app.route('/login',methods=['GET','POST'])
def login():
    user = get_current_user()
    if request.method=='POST':
        name=request.form['name']
        password=request.form['password']
        host="localhost";user="root";dbname="QandA"
        conn = pymysql.connect(host, user=user,port=3306,passwd="", db=dbname)
        cursor=conn.cursor()
        cursor.execute("SELECT id,name,password from users where name=%s",(name))
        result=cursor.fetchall()
        if check_password_hash(result[0][2],password):
            session['user']=result[0][1]

            return "<h1> The Password is Correct!</h1>"
        else:
            return "<h1> The Password is Incorrect!</h1>"
        
        # return "<h1>{}</h1>".format()
        # return "<h1>Name: {}  Pass: {}</h1>".format(name,password)
    return render_template('login.html')

@app.route('/question')
def question():
    user = get_current_user()
    return render_template('question.html')

@app.route('/answer')
def answer():
    user = get_current_user()
    return render_template('answer.html')

@app.route('/ask')
def ask():
    user = get_current_user()
    return render_template('ask.html')

@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    return render_template('unanswered.html')

@app.route('/users')
def users():
    user = get_current_user()
    return render_template('users.html')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)