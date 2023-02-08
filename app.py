from flask import Flask, request, jsonify, render_template ,make_response
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from  werkzeug.security import generate_password_hash, check_password_hash
import json
import jwt
import uuid

from flask_jwt_extended import JWTManager,create_access_token,create_refresh_token,jwt_required,get_jwt_identity

from models.models import db,Employee,Admin,Attendance,Working_days
from Duration import Duration
from datetime import date,datetime, timedelta
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)

CORS(app)
JWTManager(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:%s@localhost/smart' % quote_plus('bala')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your secret key'

db.init_app(app)

jsondecoder = json.JSONDecoder()


@app.route("/", methods=['POST', 'GET'])
def root():
    return make_response(jsonify({'message' : "Success"}), 200)



def user_details(f):
    current_user = Admin.query.filter_by(user_name=f).first()
    return current_user

#   Refresh
 
@app.route("/token/refresh" , methods = ['POST','GET'])
@jwt_required(refresh=True)
def token_refresh():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'message' : 'User Logged Out..Need to Login'}),
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

        jwt_access_token = create_access_token(identity=user_name)
        jwt_refresh_token = create_refresh_token(identity=user_name)
        
        setattr(user, "validity", 1)
        db.session.commit()
        
        return make_response(
            jsonify({"status" : "Success", "access_token" : jwt_access_token , "refresh_token" : jwt_refresh_token , "token_expire_time" : 15}),
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
        jsonify({'message' : 'User Logged Out..Need to Login'}),
        401)
    
    setattr(current_user, "validity", 0)
    db.session.commit()
    return make_response(
        jsonify({'message' : 'Logged Out',"user_name" : current_user.user_name}),
        200)

#   Employee_Details

@app.route("/employee_details", methods = ['POST','GET'])
@jwt_required()
def employee_details():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'message' : 'User Logged Out..Need to Login'}),
        401)
        
    data = request.form
    
    if not data or not data.get('email') or not data.get('first_name') or not data.get('last_name') or not data.get('dob') or not data.get('designation'):
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401
            )

    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    dob = data.get('dob')
    designation = data.get('designation')

    birthdate = datetime.strptime(dob , "%Y-%m-%d")
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    
    user = Employee.query.filter_by(first_name=first_name).filter_by(last_name=last_name).first() or Employee.query.filter_by(email=email).first()
    if user:
        return make_response(
            jsonify({"status" : "Employee Already Exists"}),
            401)
        
    emp_id = str(uuid.uuid4())
    record = Employee(emp_id,first_name,last_name,email,designation,dob,age)
    db.session.add(record)
    db.session.commit()
    return make_response(
            jsonify({"status" : "Successfully Inserted..."}),
            200)


#   Employee List

@app.route("/employee_list", methods = ['POST','GET'])
@jwt_required()
def employee_list():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'message' : 'User Logged Out..Need to Login'}),
        401)
    print(request.get_data())
    data = request.get_json()
    print(data)
    if not data or not data['page_number']:
        return make_response(
        jsonify({'message' : 'Feilds Missing..!'}),
        401) 
    
    page_number = int(data['page_number'])
    print("1....................",page_number)
    emp_list = Employee.query.all()

    if not emp_list:
        return make_response(
            jsonify({"status" : "No Employee Found"}),
            401)
    
    emp_list_size = len(emp_list)

    total_pages = int(emp_list_size/10)
    if total_pages%10!=0:
        total_pages+=1

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
        jsonify({'message' : 'User Logged Out..Need to Login'}),
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
        jsonify({'message' : 'User Logged Out..Need to Login'}),
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
        jsonify({'message' : 'User Logged Out..Need to Login'}),
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


#   Attendance

@app.route("/attendance_entry", methods = ['POST','GET'])
@jwt_required()
def attendance_entry():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'message' : 'User Logged Out..Need to Login'}),
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
