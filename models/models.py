from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Admin(db.Model):
    
    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key = True)
    emp_id = db.Column(db.String(256))
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


class Entry(db.Model) : 

    __tablename__ = "entry"

    id = db.Column(db.Integer, primary_key = True)
    user_name = db.Column(db.Integer , unique = True) 
    date = db.Column(db.String(50))
    entry_time_1 = db.Column(db.String(50) )
    entry_time_2 = db.Column(db.String(50) )
    entry_time_3 = db.Column(db.String(50) )
    entry_time_4 = db.Column(db.String(50) )
    entry_time_5 = db.Column(db.String(50) )
    count = db.Column(db.Integer)


    def __init__(self, user_name, date, entry_time_1, entry_time_2, entry_time_3, entry_time_4, entry_time_5 ,count) :
        self.user_name = user_name
        self.date = date
        self.entry_time_1 = entry_time_1
        self.entry_time_2 = entry_time_2
        self.entry_time_3 = entry_time_3
        self.entry_time_4 = entry_time_4
        self.entry_time_5 = entry_time_5
        self.count = count

class Attendance(db.Model) :

    __tablename__ = "attendance"
    
    id = db.Column(db.Integer , primary_key = True) 
    user_name = db.Column(db.Integer ) 
    date = db.Column(db.String(50))
    status = db.Column(db.String(10))

    def __init__(self, user_name, date ,status) :
        self.user_name = user_name  
        self.date = date 
        self.status = status 