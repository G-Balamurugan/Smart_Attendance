from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    user_name = db.Column(db.String(100))
    dob = db.Column(db.String(100))
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)
    password = db.Column(db.String(256))
    user_type = db.Column(db.String(20))
    validity = db.Column(db.Integer)

    def __init__(self, first_name, last_name, user_name, email, dob, age, user_type, password, validity):
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name
        self.email = email
        self.dob = dob
        self.age = age
        self.user_type = user_type
        self.password = password
        self.validity = validity