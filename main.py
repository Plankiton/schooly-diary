from app import app, db
from db import User

if(__name__ == '__main__'):
    app.secret_key = "ThisIsNotASecret:p"

    db.create_all()
    app.run()
