from flask import Flask, request, jsonify, render_template ,make_response
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from  werkzeug.security import generate_password_hash, check_password_hash
import json
import jwt
import uuid

from flask_jwt_extended import JWTManager,create_access_token,create_refresh_token,jwt_required,get_jwt_identity,get_jwt

from models.models import db,Employee,Admin,Attendance,Working_days,Month_attendance
from Duration import Duration
from datetime import date,datetime,timedelta
from functools import wraps
from flask_cors import CORS

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:%s@localhost/smart' % quote_plus('bala')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = 'your secret key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=3)

CORS(app)
JWTManager(app)

db.init_app(app)

jsondecoder = json.JSONDecoder()


@app.route("/", methods=['POST', 'GET'])
def root():
    return make_response(jsonify({'status' : "Success"}), 200)



def user_details(f):
    current_user = Admin.query.filter_by(user_name=f).first()
    return current_user

def employee_details(f):
    current_employee = Employee.query.filter_by(user_name=f).first()
    return current_employee


#   Employee Atendance Entry By APSCHEDULER

scheduler = BackgroundScheduler(daemon = True)

def employee_attendance():
    with app.app_context():
        employee_list_attendance = Attendance.query.all()
        
        for attendance_chk in employee_list_attendance:
        
            today = date.today()
                
            attendance_per_chk = attendance_chk.day_attendance_present / (attendance_chk.day_attendance_present + attendance_chk.day_attendance_absent)
        
            if attendance_per_chk*100<75:    
                return  make_response(
                jsonify({'status' : 'Absent..Because Below 75%'}),
                200)
            
            if attendance_chk.out_duration>7200:
                return  make_response(
                jsonify({'status' : 'Absent..Out time more than 2hour'}),
                200)
            
            employee_chk = Employee.query.filter_by(emp_id=attendance_chk.emp_id).first()
            month_attendance_update = Month_attendance.query.filter_by(emp_id=attendance_chk.emp_id).filter_by(month_number=attendance_chk.month).first()
            month_chk = Working_days.query.filter_by(month_number=today.month).first()
            if not month_chk:
                return  make_response(
                jsonify({'status' : 'No entry for workingday..!'}),
                401)
                
            attendance_perc=((month_attendance_update.days_present+1)/(month_chk.working_days_count))    

            setattr(employee_chk,"current_attendance_percentage",attendance_perc)
            setattr(month_attendance_update,"days_present",month_attendance_update.days_present+1)
            db.session.commit()    
            
            db.session.delete(attendance_chk)
            db.session.commit()
        
        print("Attendance..Updated..!")

job = scheduler.add_job(employee_attendance, 'cron', hour='15', minute='10',second='00')

scheduler.start()


#   Refresh
 
@app.route("/token/refresh" , methods = ['POST','GET'])
@jwt_required(refresh=True)
def token_refresh():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
    
    access_token = create_access_token(identity=current_user.user_name)

    return make_response(
            jsonify({"status" : "Success", "access_token" : access_token }),
            200)

#   Admin

@app.route("/admin/insert" , methods = ['POST','GET'])
def login_insert():
    data = request.form
    
    if not data or not data.get('user_name') or not data.get('password') or not data.get('email') :
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401)
    if not data.get('first_name') or not data.get('last_name') or not data.get('dob') or not data.get('designation'):
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401)
    
    password = data.get('password')       
    user_name , email = data.get('user_name') , data.get('email')
    first_name , last_name = data.get('first_name') , data.get('last_name')
    designation = data.get('designation')
    dob = data.get('dob')

    birthdate = datetime.strptime(dob , "%Y-%m-%d")
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    user = Admin.query.filter_by(user_name=user_name).first() or  Admin.query.filter_by(email=email).first()
    if user:
        return make_response(
            jsonify({"status" : "User Already Exists"}),
            401)
    
    password= generate_password_hash(data["password"])
    admin_id = str(uuid.uuid4())
    record = Admin(admin_id,first_name,last_name,dob,age,designation,email,user_name,password,0)
    db.session.add(record)
    db.session.commit()
    return make_response(
            jsonify({"status" : "Successfully Inserted.." ,"user_name" : user_name}),
            200)
    
   
#   Login

@app.route("/login" , methods = ['POST','GET'])
def login():
    data = request.form
    
    if not data or not data.get('username') or not data.get('password'):
        return make_response(
            jsonify({"status" : "Feilds missing"}),
            401)
        
    user_name = data.get('username')
    password = data.get('password')
    
    user = Admin.query.filter_by(user_name = user_name).first()
    if not user:
        return make_response(
            jsonify({"status" : "User not found"}),
            401)
    
    if check_password_hash(user.password, password):

        jwt_access_token = create_access_token(identity=user_name,expires_delta=timedelta(hours=2))
        jwt_refresh_token = create_refresh_token(identity=user_name,expires_delta=timedelta(hours=3))
    
        setattr(user, "validity", 1)
        db.session.commit()
        
        return make_response(
            jsonify({"status" : "Success", "access_token" : jwt_access_token , "refresh_token" : jwt_refresh_token , "token_expire_time" : 7200}),
            200)
    else:
        return make_response(
            jsonify({"status" : "Wrong password"}),
            401)

#   Logout

@app.route("/logout" , methods=['POST','GET'])
@jwt_required()
def logout():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
    
    setattr(current_user, "validity", 0)
    db.session.commit()
    return make_response(
        jsonify({'status' : 'Logged Out',"user_name" : current_user.user_name}),
        200)

#   Employee_Details_Insert

@app.route("/employee_details", methods = ['POST','GET'])
@jwt_required()
def employee_details_insert():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
        
    data = request.form
    
    if not data or not data.get('email') or not data.get('firstName') or not data.get('lastName') or not data.get('dob') or not data.get('designation') or not data.get('userName') or not data.get('password'):
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401)

    email = data.get('email')
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    dob = data.get('dob')
    designation = data.get('designation')
    user_name = data.get('userName')
    password= generate_password_hash(data.get("password"))
        
    birthdate = datetime.strptime(dob , "%Y-%m-%d")
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    user = Employee.query.filter_by(first_name=first_name).filter_by(last_name=last_name).first() or Employee.query.filter_by(email=email).first()
    if user:
        return make_response(
            jsonify({"status" : "Employee Already Exists"}),
            401)
    
    user_name_chk = Employee.query.filter_by(user_name=user_name).first()
    if user_name_chk:
        return make_response(
            jsonify({"status" : "User Name Already Exists"}),
            401)
        
    emp_id = str(uuid.uuid4())
    record = Employee(emp_id,first_name,last_name,email,designation,dob,age,user_name,password,0)
    db.session.add(record)
    db.session.commit()
    
    employee_details_chk = Employee.query.filter_by(emp_id=emp_id).first()
    setattr(employee_details_chk,"current_attendance_percentage",0)
    db.session.commit()
    
    return make_response(
            jsonify({"status" : "Successfully Inserted..."}),
            200)


#   Employee Login App

@app.route("/employee/login" , methods = ['POST','GET'])
def employee_login():
    data = request.form
    
    if not data or not data.get('userName') or not data.get('password'):
        return make_response(
            jsonify({"status" : "Feilds missing"}),
            401)
        
    user_name = data.get('userName')
    password = data.get('password')
    
    user = Employee.query.filter_by(user_name=user_name).first()
   
    if not user:
        return make_response(
            jsonify({"status" : "Employee not found"}),
            401)
    
    if check_password_hash(user.password, password):

        jwt_access_token_employee = create_access_token(identity=user_name,expires_delta=timedelta(hours=2))
        jwt_refresh_token_employee = create_refresh_token(identity=user_name,expires_delta=timedelta(hours=3))
        
        employee_chk_attendance = Attendance.query.filter_by(emp_id=user.emp_id).first()
        if not employee_chk_attendance:
            today = datetime.today()
            record = Attendance(user.emp_id,user.first_name,today.day,today.month,today.year,0,0,"","",0) 
            db.session.add(record)
        
        today = date.today()
        
        employee_month_chk = Month_attendance.query.filter_by(emp_id=user.emp_id).filter_by(month_number=today.month).first()
        if not employee_month_chk:
            record_ = Month_attendance(user.emp_id,today.month,0) 
            db.session.add(record_)
        db.session.commit()
        
        setattr(user, "validity", 1)
        db.session.commit()
        
        return make_response(
            jsonify({"status" : "Success", "access_token" : jwt_access_token_employee , "refresh_token" : jwt_refresh_token_employee , "token_expire_time" : 7200}),
            200)
    else:
        return make_response(
            jsonify({"status" : "Wrong password"}),
            401)


#   Employee Logout App

@app.route("/employee/logout" , methods=['POST','GET'])
@jwt_required()
def employee_logout():
    current_user = employee_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
    
    setattr(current_user, "validity", 0)
    db.session.commit()
    return make_response(
        jsonify({'status' : 'Logged Out',"user_name" : current_user.user_name}),
        200)

#   Employee List

@app.route("/employee_list", methods = ['POST','GET'])
@jwt_required()
def employee_list():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
    
    data = request.get_json()
    
    if not data or not data['page_number']:
        return make_response(
        jsonify({'status' : 'Feilds Missing..!'}),
        401) 
    
    page_number = int(data['page_number'])
    
    emp_list = Employee.query.all()

    if not emp_list:
        return make_response(
            jsonify({"status" : "No Employee Found"}),
            401)
    
    emp_list_size = len(emp_list)

    total_pages = int(emp_list_size/10)
    #print("11...............",total_pages)
    if total_pages%10!=0 or total_pages==0:
        total_pages+=1
    #print("22..................",total_pages)
    if total_pages<(page_number-1):
        return make_response(
            jsonify({"status" : "Page Limit Exceeded..!"}),
            401)
    
    output_range_start = (page_number*10) - 10
    output_range_end = page_number*10
    
    if output_range_end>emp_list_size:
        output_range_end = output_range_start + (emp_list_size%10) 
    
    final_result = {}
    final_result['total_pages'] = total_pages
    
    result=[]
    for i in range(output_range_start,output_range_end):
        temp={}
        temp['employee_name']=emp_list[i].first_name
        temp['designation']=emp_list[i].designation
        result.append(temp)
    
    final_result['employee_list'] = result

    return final_result


#   Employee Search

@app.route("/employee_search", methods = ['POST','GET'])
@jwt_required()
def employee_search():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
        
        
    data = request.get_json()
    
    if not data or not data['employee_name']:
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401)
        
    employee_details_search = Employee.query.filter_by(first_name=data['employee_name']).first()
    
    if not employee_details_search:
        return make_response(
            jsonify({"status" : "No Match Found..!"}),
            401)
        
    output={}
    output['employee_name'] = employee_details_search.first_name
    output['designation'] = employee_details_search.designation
    
    return output
    
    
#   Employee Select

@app.route("/employee_select", methods = ['POST','GET'])
@jwt_required()
def employee_select():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
    
    #print(request.get_data())
    data = request.get_json()
    #print(data)
    if not data or not data['employee_name'] or not data['designation']:
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401)
        
    employee_details_search = Employee.query.filter_by(first_name=data['employee_name']).filter_by(designation=data['designation']).first()
    
    if not employee_details_search:
        return make_response(
            jsonify({"status" : "No Match Found..!"}),
            401)
        
    today = date.today()
    
    attendance_perc_chk = Attendance.query.filter_by(id=employee_details_search.id).filter_by(employee_name=employee_details_search.first_name).all()

    attendance_perc = 0
    for i in attendance_perc_chk:
        if i.day_attendance=="present":
            attendance_perc+=1
        
    month_chk = Working_days.query.filter_by(month_number=today.month).first()
    print(attendance_perc)
    attendance_perc=(attendance_perc/(month_chk.working_days_count))
    print(attendance_perc)
    
    output={}
    output['emp_id']=employee_details_search.emp_id
    output['first_name']=employee_details_search.first_name
    output['last_name']=employee_details_search.last_name
    output['dob']=employee_details_search.dob
    output['age']=employee_details_search.age
    output['email']=employee_details_search.email
    output['designation']=employee_details_search.designation
    output['attendance_percent']=str(attendance_perc)+"%"
    
    print(output)
    return output


#   Working_days

@app.route("/working_days", methods = ['POST','GET'])
@jwt_required()
def working_days():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
        
    data = request.form
    
    if not data or not data.get('month') or not data.get('number_of_days'):
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401)
    
    month_number = int(data.get('month'))
    number_of_days = int(data.get('number_of_days'))
    
    today = date.today()
    curr_year = today.year
    
    if (month_number%2==1 and number_of_days>31) or (month_number>12 and month_number<1):
        return make_response(
            jsonify({"status" : "Invalid Entry.."}),
            401)
    
    elif number_of_days>30 or (month_number%2==0 and number_of_days>28) or ():
        return make_response(
            jsonify({"status" : "Invalid Entry.."}),
            401)
    
    elif (month_number==2) and ((curr_year%4==0 and curr_year%100!=0) or curr_year%400==0) and number_of_days>29:
        return make_response(
            jsonify({"status" : "Invalid Entry.."}),
            401)
    
    month_chk = Working_days.query.filter_by(month_number=month_number).first()
    
    if month_chk:
        setattr(month_chk, "working_days_count", number_of_days)
    else:
        record = Working_days(month_number,number_of_days)
        db.session.add(record)
    
    db.session.commit()
    return make_response(
            jsonify({"status" : "Successfully Inserted.."}),
            200)


#   Employee Details Display

@app.route("/employee/details_select", methods = ['POST','GET'])
@jwt_required()
def employee_details_select():

    current_user = employee_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
    
    output = {}
    
    output['emp_id']=current_user.emp_id
    output['first_name']=current_user.first_name
    output['last_name']=current_user.last_name
    output['dob']=current_user.dob
    output['age']=current_user.age
    output['email']=current_user.email
    output['designation']=current_user.designation
    
    return output


#   Present
 
@app.route("/present", methods = ['POST','GET'])
@jwt_required()
def employee_present():
    current_user = employee_details(get_jwt_identity())
    #print("11...................",current_user)
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
    
    employee_chk = Employee.query.filter_by(emp_id=current_user.emp_id).first()
    
    if not employee_chk:
        return make_response(
            jsonify({"status" : "Invalid Employee Details"}),
            401)

    employee_chk_attendance = Attendance.query.filter_by(emp_id=current_user.emp_id).first()
    
    setattr(employee_chk_attendance,"day_attendance_present",employee_chk_attendance.day_attendance_present +1)
    db.session.commit()
    
    return make_response(
        jsonify({"status" : "Successfully Updated.."}),
        200)


#   Absent
 
@app.route("/absent", methods = ['POST','GET'])
@jwt_required()
def employee_absent():
    current_user = employee_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)

    employee_chk = Employee.query.filter_by(emp_id=current_user.emp_id).first()
    
    if not employee_chk:
        return make_response(
            jsonify({"status" : "Invalid Employee Details"}),
            401)

    employee_chk_attendance = Attendance.query.filter_by(emp_id=current_user.emp_id).first()
    
    setattr(employee_chk_attendance,"day_attendance_absent",employee_chk_attendance.day_attendance_absent +1)
    db.session.commit()
    
    return make_response(
        jsonify({"status" : "Successfully Updated.."}),
        200)


#   In Time

@app.route("/in_time", methods = ['POST','GET'])
@jwt_required()
def employee_in():
    current_user = employee_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
    
    employee_chk = Employee.query.filter_by(emp_id=current_user.emp_id).first()
    
    if not employee_chk:
        return make_response(
            jsonify({"status" : "Invalid Employee Details"}),
            401)

    employee_chk_attendance = Attendance.query.filter_by(emp_id=current_user.emp_id).first()
    
    setattr(employee_chk_attendance,"in_time",str(datetime.now()))
    db.session.commit()
    print(str(datetime.now()))
    if employee_chk_attendance.out_time != "":
        duration_left = Duration.duration_left(employee_chk_attendance.out_time,str(datetime.now()))
        setattr(employee_chk_attendance,"out_duration",employee_chk_attendance.out_duration + duration_left)
        setattr(employee_chk_attendance,"in_time","")
        setattr(employee_chk_attendance,"out_time","")
        db.session.commit()
        
    return make_response(
        jsonify({"status" : "Successfully Updated.."}),
        200)


#   Out Time

@app.route("/out_time", methods = ['POST','GET'])
@jwt_required()
def employee_out():
    current_user = employee_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
    
    employee_chk = Employee.query.filter_by(emp_id=current_user.emp_id).first()
    
    if not employee_chk:
        return make_response(
            jsonify({"status" : "Invalid Employee Details"}),
            401)

    employee_chk_attendance = Attendance.query.filter_by(emp_id=current_user.emp_id).first()
    
    setattr(employee_chk_attendance,"out_time",str(datetime.now()))
    db.session.commit()
    
    return make_response(
        jsonify({"status" : "Successfully Updated.."}),
        200)


#   Attendance

@app.route("/attendance_entry", methods = ['POST','GET'])
@jwt_required()
def attendance_entry():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'status' : 'User Logged Out..Need to Login'}),
        401)
        
    data = request.form

    if not data or not data.get('emp_id') or not data.get('name') or not data.get('date') or not data.get('attendance'):
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401)
    
    emp_id = data.get('emp_id')
    employee_name = data.get('name')
    attendance_date_given = data.get('date')
    attendance = data.get('attendance')
    
    emp_chk = Employee.query.filter_by(id=emp_id).filter_by(first_name=employee_name).first()
    
    if not emp_chk:
        return make_response(
            jsonify({"status" : "Invalid Employee Details"}),
            401)
    if attendance!='present' and attendance!="absent":
        return make_response(
            jsonify({"status" : "Invalid Entry...Enter present or absent..."}),
            401)
    
    attendance_date = datetime.strptime(attendance_date_given , "%Y-%m-%d")
    today = date.today()
    
    if today.year<attendance_date.year or today.month<attendance_date.month or (today.month==attendance_date.month and today.day<attendance_date.day):
        return make_response(
            jsonify({"status" : "Invalid Date.."}),
            401)
    
    month_chk = Working_days.query.filter_by(month_number=attendance_date.month).first()
    if not month_chk:
        return make_response(
            jsonify({"status" : "Entry Missing in Working Days Table..!"}),
            401)

    attendance_chk = Attendance.query.filter_by(employee_name=employee_name).filter_by(emp_id=emp_id).filter_by(day=attendance_date.day).filter_by(month=attendance_date.month).filter_by(year=attendance_date.year).first()
    print(attendance_chk)    
    if attendance_chk:
        setattr(attendance_chk,"day_attendance",attendance)
        db.session.commit()
    
        return make_response(
            jsonify({"status" : "Successfully Updated.."}),
            200)

    else:
        record = Attendance(emp_id, employee_name, attendance_date.day, attendance_date.month, attendance_date.year, attendance)
        db.session.add(record)
        db.session.commit()
    
        return make_response(
            jsonify({"status" : "Successfully Inserted.."}),
            200)
