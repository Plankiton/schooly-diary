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
    if sign_type not in ['student', 'teacher']:
        return redirect('/not_found', code=404)

    if request.method == 'POST':
        person = request.form.to_dict()
        person['type'] = sign_type
        print(person)

        remove_list = []
        notification_emails = []
        for key in person:
            if 'notification_email' in key:
                notification_emails.append(person[key])
                remove_list.append(key)
        for key in remove_list:
            del person[key]
        if 'notification_email_count' in person:
            del person['notification_email_count']
        person['notification_emails'] = notification_emails

        print(person)
        try:
            inserted = persons.insert_one(person)
            if sign_type == 'student':
                redirect(url_for('/student', id=inserted.inserted_id))
            return redirect(url_for('login'))
        except:
            return render_template('index.html', message='User Already Exists')
    else:
        return render_template('register.html', sign_type=sign_type)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        e = request.form['email']
        p = request.form['password']
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

if __name__ == '__main__':
    app.run()
