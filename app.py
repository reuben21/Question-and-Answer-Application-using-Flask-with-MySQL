from flask import *

from werkzeug.security import generate_password_hash, check_password_hash

import pymysql

import os

try:
    host = "localhost"
    user = "root"
    dbname = "QandA"
    conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
    cursor = conn.cursor()
except Exception as e:
    print(e)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


def get_current_user():
    user_dict = {}

    user_result = None
    if 'user' in session:
        user = session['user']
        conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
        cursor = conn.cursor()
        cursor.execute("SELECT * from users where name=%s", (user))
        user_result = cursor.fetchall()
        user_dict['id'] = int(user_result[0][0])
        user_dict['name'] = user_result[0][1]
        user_dict['admin'] = int(user_result[0][4])
        user_dict['expert'] = int(user_result[0][3])

        print(user_dict)
        # print("user cursor",user_result)
    return user_dict


@app.route('/')
def index():
    user_dict = get_current_user()
    conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
    cursor = conn.cursor()
    cursor.execute("""select questions.id as question_id, questions.question_text, askers.name as asker_name, experts.name as expert_name 
                        from questions 
                        join users as askers on askers.id = questions.asked_by_id 
                        join users as experts on experts.id = questions.expert_id 
                        where questions.answer_text is not null; """)
    Answered_questions = cursor.fetchall()
    answer_list = []
    for i in Answered_questions:
        dict1 = {}
        dict1['q_id'] = i[0]
        dict1['q_text'] = i[1]
        dict1['answer_name'] = i[2]
        dict1['expert_name'] = i[3]
        answer_list.append(dict1)

    return render_template('home.html', user=user_dict, question=answer_list)


@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        conn1 = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
        cursor1 = conn1.cursor()
        cursor1.execute("select id from users where name=%s", (name))
        check_id = cursor1.fetchall()
        conn1.commit()
        print(check_id)
        try:
            print(name)
            if check_id:
                print("The Check ID is :", check_id)
                return render_template('register.html', user=user, error="Username Already Exists")

            else:
                hashed_password = generate_password_hash(password, method="sha256")
                host = "localhost";
                user = "root";
                dbname = "QandA"
                conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
                cursor = conn.cursor()
                cursor.execute("INSERT into users(name,password,expert,admin) values (%s,%s,%s,%s)",
                               (name, hashed_password, 0, 0))
                conn.commit()
                conn.close()
                session['user'] = name
                return redirect(url_for('index'))
        except IndexError:
            return render_template('register.html', user=user, error="You havent Entered A Username")

    return render_template('register.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        host = "localhost";
        user23 = "root";
        dbname = "QandA"
        conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
        cursor = conn.cursor()
        cursor.execute("SELECT id,name,password from users where name=%s", (name))
        result = cursor.fetchall()
        if check_password_hash(result[0][2], password):
            session['user'] = result[0][1]

            return redirect(url_for('index'))
        else:
            return "<h1> The Password is Incorrect!</h1>"

        # return "<h1>{}</h1>".format()
        # return "<h1>Name: {}  Pass: {}</h1>".format(name,password)

    return render_template('login.html', user=user)


@app.route('/question/<question_id>')
def question(question_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
    cursor = conn.cursor()
    cursor.execute("""select questions.question_text, questions.answer_text, askers.name as asker_name, experts.name as expert_name 
                    from questions 
                    join users as askers on askers.id = questions.asked_by_id 
                    join users as experts on experts.id = questions.expert_id 
                    where questions.id =%s; """, (question_id))
    result = cursor.fetchall()
    answer_list = []
    for i in result:
        dict1 = {}
        dict1['q_text'] = i[0]
        dict1['answer_text'] = i[1]
        dict1['asker_name'] = i[2]
        dict1['expert_name'] = i[3]
        answer_list.append(dict1)
    return render_template('question.html', user=user, question=answer_list)


@app.route('/answer/<question_id>', methods=['GET', 'POST'])
def answer(question_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == "POST":
        answer = request.form['answer']
        conn1 = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
        cursor1 = conn1.cursor()
        cursor1.execute("Update questions set answer_text=%s where id=%s", (answer, question_id))
        conn1.commit()
        conn1.close()
        return redirect(url_for('unanswered'))
    conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
    cursor = conn.cursor()
    cursor.execute("select id,question_text from questions where id=%s", (question_id))
    question = cursor.fetchall()
    print(question)
    question_list = []
    for i in question:
        quest_dict = {}
        quest_dict['id'] = int(i[0])
        quest_dict['name'] = i[1]
        question_list.append(quest_dict)
    return render_template('answer.html', user=user, question=quest_dict)


@app.route('/ask', methods=['GET', 'POST'])
def ask():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    if request.method == 'POST':
        print(user)
        Question = request.form['question']
        ExpertId = request.form['expert']
        conn1 = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
        cur = conn1.cursor()
        cur.execute("INSERT into questions (question_text,asked_by_id, expert_id) values(%s,%s,%s);",
                    (Question, user['id'], ExpertId))
        conn1.commit()
        conn1.close()

    conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
    cursor = conn.cursor()
    cursor.execute("SELECT id,name from users where expert=1")
    expert_result = cursor.fetchall()
    # print("expert result:",expert_result[0][1])
    expert_list = []

    for i in expert_result:
        print(i)
        expert_dict = {}
        expert_dict['id'] = i[0]
        expert_dict['name'] = i[1]
        expert_list.append(expert_dict)
    print(expert_list)
    return render_template('ask.html', user=user, experts=expert_list)


@app.route('/unanswered')
def unanswered():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT questions.id,questions.question_text,users.name from questions join users on users.id=questions.asked_by_id where questions.answer_text is null and questions.expert_id=%s",
        (user['id']))
    qcurse = cursor.fetchall()
    question_list = []
    for i in qcurse:
        quest_dict = {}
        quest_dict['id'] = i[0]
        quest_dict['question'] = i[1]
        quest_dict['asked_by_id'] = i[2]
        question_list.append(quest_dict)
    return render_template('unanswered.html', user=user, questions=question_list)


@app.route('/users')
def users():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
    cursor = conn.cursor()
    cursor.execute("Select id ,name,expert,admin from users")
    results = cursor.fetchall()
    users_list = []
    for i in results:
        quest_dict = {}
        quest_dict['id'] = int(i[0])
        quest_dict['name'] = i[1]
        quest_dict['expert'] = int(i[2])
        quest_dict['admin'] = int(i[3])
        users_list.append(quest_dict)
    print(users_list)
    return render_template('users.html', user=user, users=users_list)


@app.route('/promote/<user_id>')
def promote(user_id):
    print(user_id)
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    conn = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
    cursor = conn.cursor()
    cursor.execute("Update users set expert=1 where id =%s", (user_id))
    conn.commit()
    conn.close()
    conn1 = pymysql.connect(host="localhost", user="root", port=3306, passwd="", db="QandA")
    cursor1 = conn1.cursor()
    cursor1.execute("Select id ,name,expert,admin from users")
    results = cursor1.fetchall()
    users_list = []
    for i in results:
        quest_dict = {}
        quest_dict['id'] = int(i[0])
        quest_dict['name'] = i[1]
        quest_dict['expert'] = int(i[2])
        quest_dict['admin'] = int(i[3])
        users_list.append(quest_dict)
    print(users_list)
    return render_template('users.html', user=user, users=users_list)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
