from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
    
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key = True)
    emp_id = db.Column(db.String(256))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    user_name = db.Column(db.String(100))
    dob = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)

    def __init__(self,emp_id, first_name, last_name, email, designation, dob, age):
        self.emp_id = emp_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.designation = designation
        self.dob = dob
        self.age = age


class Login(db.Model):
    
    __tablename__ = "login"
    
    id = db.Column(db.Integer, primary_key = True) 
    user_name = db.Column(db.String(100))
    password = db.Column(db.String(256))
    validity = db.Column(db.Integer)
    
    def __init__(self,user_name,password,validity):
        self.user_name = user_name
        self.password = password
        self.validity = validity