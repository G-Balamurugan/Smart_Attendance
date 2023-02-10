from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
    
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key = True)
    emp_id = db.Column(db.String(256))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    dob = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)
    user_name = db.Column(db.String(100))
    password = db.Column(db.String(256))
    current_attendance_percentage = db.Column(db.Integer)
    validity = db.Column(db.Integer)
    
    def __init__(self,emp_id, first_name, last_name, email, designation, dob, age , user_name ,password ,validity):
        self.emp_id = emp_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.designation = designation
        self.dob = dob
        self.age = age
        self.user_name = user_name
        self.password = password
        self.validity = validity

class Admin(db.Model):
    
    __tablename__ = "admin"
    
    id = db.Column(db.Integer, primary_key = True) 
    admin_id = db.Column(db.String(256))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    user_name = db.Column(db.String(100))
    password = db.Column(db.String(256))
    validity = db.Column(db.Integer)
    dob = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    email = db.Column(db.String(100))
    age = db.Column(db.Integer)
    
    def __init__(self,admin_id, first_name, last_name, dob, age, designation, email, user_name,password,validity):
        self.admin_id = admin_id
        self.first_name = first_name
        self.last_name = last_name
        self.dob = dob
        self.age = age
        self.designation = designation
        self.email = email
        self.user_name = user_name
        self.password = password
        self.validity = validity
        
class Attendance(db.Model):
    
    __tablename__ = "attendance"
    
    id = db.Column(db.Integer, primary_key = True) 
    emp_id = db.Column(db.String(256))
    employee_name = db.Column(db.String(100))
    day = db.Column(db.Integer)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    day_attendance_present = db.Column(db.Integer)
    day_attendance_absent = db.Column(db.Integer)
    in_time = db.Column(db.String(100))
    out_time = db.Column(db.String(100))
    out_duration = db.Column(db.Integer)
    
    def __init__(self,emp_id,employee_name,day,month,year,day_attendance_present,day_attendance_absent,in_time,out_time,out_duration):
        self.emp_id = emp_id
        self.employee_name = employee_name
        self.day_attendance_present = day_attendance_present
        self.day_attendance_absent = day_attendance_absent
        self.in_time = in_time
        self.out_time = out_time
        self.out_duration = out_duration
        self.day = day
        self.month = month
        self.year = year

class Working_days(db.Model):
    
    __tablename__ = "working_days"
      
    id = db.Column(db.Integer, primary_key = True)
    month_number = db.Column(db.Integer)
    working_days_count = db.Column(db.Integer)
    
    def __init__(self,month_number,working_days_count):
        self.month_number = month_number
        self.working_days_count = working_days_count

class Month_attendance(db.Model):
    
    __tablename__ = "month_attendance"
      
    id = db.Column(db.Integer, primary_key = True)
    emp_id = db.Column(db.String(256))
    month_number = db.Column(db.Integer)
    days_present = db.Column(db.Integer)
    
    def __init__(self,emp_id,month_number,days_present):
        self.emp_id = emp_id
        self.month_number = month_number
        self.days_present = days_present