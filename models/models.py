from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key = True)
    emp_id = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    user_name = db.Column(db.String(100))
    dob = db.Column(db.String(100))
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)
    password = db.Column(db.String(256))
    validity = db.Column(db.Integer)

    def __init__(self,emp_id, first_name, last_name, user_name, email, dob, age, password, validity):
        self.emp_id = emp_id
        self.first_name = first_name
        self.last_name = last_name
        self.user_name = user_name
        self.email = email
        self.dob = dob
        self.age = age
        self.password = password
        self.validity = validity