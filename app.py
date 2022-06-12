from flask import Flask, url_for, render_template, request, redirect, session
from jinja2 import environment
from pymongo import MongoClient
from os import environ, getenv
from dotenv import load_dotenv
load_dotenv()

database_uri = getenv('DATABASE_URI')
if not database_uri:
    database_uri = 'mongodb://diary:diary@0.0.0.0:27017'
database_name = getenv('DATABASE_NAME')
if not database_name:
    database_name = 'diary'

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
db = MongoClient(database_uri)
diary_db = db[database_name]

persons = diary_db.persons
diarys = diary_db.diarys
classes = diary_db.classes

@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('home.html')
    else:
        return render_template('index.html', message='Hello!')


@app.route('/register/<sign_type>', methods=['GET', 'POST'])
def register(sign_type):
    if sign_type not in ['student', 'teacher', "class"]:
        return redirect('/not_found', code=404)

    if request.method == 'POST':
        if sign_type == "class":
            st_class = request.form.to_dict()

            students = []
            remove = []
            for key in st_class:
                if "id" in key:
                    print(key)
                    students.append(key[key.index(".")+1:])
                    remove.append(key)
            for key in remove:
                del st_class[key]

            st_class["students"] = students
            inserted = classes.insert_one(st_class)
            return redirect(url_for('get_' + sign_type, id=inserted.inserted_id))

        person = request.form.to_dict()
        person['type'] = sign_type

        remove_list = []
        notification_emails = []
        if 'notification_email_count' in person:
            del person['notification_email_count']
        for key in person:
            if 'notification_email' in key:
                notification_emails.append(person[key])
                remove_list.append(key)
        for key in remove_list:
            del person[key]
        person['notification_emails'] = notification_emails

        try:
            inserted = persons.insert_one(person)
            if sign_type == 'teacher':
                return redirect(url_for('login'))
            return redirect(url_for('get_' + sign_type, id=inserted.inserted_id))
        except:
            return render_template('index.html', message='User Already Exists')
    else:
        students_res = persons.find({ "type": "student" })
        students = []
        if sign_type == "class":
            if students_res:
                for st in students_res:
                    print(st)
                    students.append(dict(st))
                i = 0
                for student in students:
                    student["old"] = 19
                    student["class"] = "2 - A"
                    students[i] = student
                    i += 1
        return render_template('register.html', sign_type=sign_type, students=students)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        e = request.form['email']
        p = request.form['password']
        print(e, p)
        data = persons.find_one({"email": e, "password": p, "type": "teacher"})
        print(data)
        if data is not None:
            session['logged_in'] = True
            return redirect(url_for('index'))
        return render_template('index.html', message='Incorrect Details')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

# @app.route('/<sign_type>/<id>')
# def student(sign_type, id):
#     print(sign_type, id)
#     return f'{sign_type}/{id}'
@app.route('/student/<id>')
def get_student(id):
    return f'student/{id}'
@app.route('/class/<id>')
def get_class(id):
    return f'/class/{id}'
@app.route('/teacher/<id>')
def get_teacher(id):
    return f'/teacher/{id}'


if __name__ == '__main__':
    app.run()
