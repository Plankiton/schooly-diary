from flask import Flask, url_for, render_template, request, redirect, session, abort
from bson.objectid import ObjectId
from urllib import parse as url_encode
from jinja2 import environment
from pymongo import MongoClient
from os import environ, getenv
from dotenv import load_dotenv
from validators import validate_class, validate_students, validate_person
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
    teacher = session.get('logged_in')
    if teacher:
        class_list = []
        res = classes.find({"teacher_id": ObjectId(teacher["_id"])})
        for clas in res:
            clas["student_count"] = len(clas["students"])
            class_list.append(dict(clas))
        return render_template('home.html', teacher=teacher, classes=class_list)
    else:
        return render_template('index.html', message='Bem vindo ao Diário Escolar professor!')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', message="Pagina não encontrada"), 404

@app.route('/register/<sign_type>', methods=['GET', 'POST'])
def register(sign_type):
    accepted_subpaths = ['student', 'teacher', "class", "diary"]
    if sign_type not in accepted_subpaths:
        abort(404, description=f"Register just support {accepted_subpaths}")
        
    teacher = session["logged_in"]
    if not teacher and sign_type != "teacher":
        return redirect(url_for('login') + "?next=" + url_encode.quote("/register/"+sign_type), code=401)

    if request.method == 'POST':
        if sign_type == "class":
            st_class = request.form.to_dict()

            st_class = validate_class(st_class)
            students = st_class["students"]
            del st_class["students"]

            inserted = classes.insert_one(st_class)
            for st in students:
                student = persons.find(st)
                student = dict(student)
                student["class_id"] = ObjectId(inserted.inserted_id)
                persons.update_one({"_id": student["_id"]}, student, True)
            return redirect(url_for('get_' + sign_type, id=inserted.inserted_id))

        person = request.form.to_dict()
        person['type'] = sign_type

        person = validate_person(person)
        try:
            inserted = persons.insert_one(person)
            if sign_type == 'teacher':
                return redirect(url_for('login'))
            return redirect(url_for('get_' + sign_type, id=inserted.inserted_id))
        except:
            return render_template('index.html', message='User Already Exists')
    else:
        students_res = persons.find({ "type": "student" })
        students = validate_students(students_res)

        i = 0
        for student in students:
            if "class_id" in student:
                sel_class = classes.find_one({"_id": student["class_id"]})
                student["class"] = dict(sel_class)
            students[i] = student
            i += 1

        if sign_type != "class":
            students = []
        return render_template('register.html', sign_type=sign_type, students=students)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    next = request.args.get("next")
    if next:
       next = url_encode.quote(next)
    else:
        next = url_for('index')

    if request.method == 'GET':
        return render_template('login.html', next=next)
    else:
        e = request.form['email']
        p = request.form['password']
        data = persons.find_one({"email": e, "password": p, "type": "teacher"})
        if data is not None:
            data = dict(data)
            data["_id"] = str(data['_id'])
            session['logged_in'] = data
            return redirect(next)
        return render_template('index.html', message='Senha ou email incorretos!')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = None
    return redirect(url_for('index'))

# @app.route('/<sign_type>/<id>')
# def student(sign_type, id):
#     print(sign_type, id)
#     return f'{sign_type}/{id}'
@app.route('/student/<id>')
def get_student(id):
    return f'student/{id}'

@app.route('/diary/<id>')
def get_diary(id):
    return f'diary/{id}'

@app.route('/class/<id>')
def get_class(id):
    sel_class = classes.find_one({"_id": ObjectId(id)})
    sel_class["student_count"] = len(sel_class["students"])

    students_res = persons.find({"class_id": ObjectId(id)})
    students = validate_students(students_res)
    return render_template('class.html', sel_class=sel_class, students=students)
    
@app.route('/teacher/<id>')
def get_teacher(id):
    return f'/teacher/{id}'


if __name__ == '__main__':
    from sys import argv as args
    port = getenv("PORT") 
    if len(args)>1:
        port = args[1]
    app.run(port=int(port if port is not None else 5000))
