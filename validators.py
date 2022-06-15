from datetime import datetime
from bson.objectid import ObjectId

def validate_class(st_class):
    students = []
    remove = []
    for key in st_class:
        if "id" in key:
            students.append(key[key.index(".")+1:])
            remove.append(key)
    for key in remove:
        del st_class[key]

    st_class["students"] = [{"_id": ObjectId(id)} for id in students]
    st_class["teacher_id"] = teacher["_id"]
    return st_class

def validate_person(person):
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
    return person

def validate_students(students_res):
    students = []
    if students_res:
        for st in students_res:
            students.append(dict(st))
        i = 0
        for student in students:
            student["old"] = datetime.now().year - datetime.strptime(student["birth_date"], "%Y-%m-%d").year
            students[i] = student
            i += 1
    return students
