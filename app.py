from flask import Flask, request, jsonify, render_template ,make_response
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from  werkzeug.security import generate_password_hash, check_password_hash
import json
import jwt
import uuid

from flask_jwt_extended import JWTManager,create_access_token,create_refresh_token,jwt_required,get_jwt_identity

from models.models import db,Employee,Admin
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
@jwt_required()
def login_insert():
    current_user = user_details(get_jwt_identity())
    if current_user.validity == 0:
        return make_response(
        jsonify({'message' : 'User Logged Out..Need to Login'}),
        401)
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
            jsonify({"status" : "Successfully Inserted.." ,"user_name" : current_user.user_name}),
            200)
    
   
#   Login

@app.route("/login" , methods = ['POST','GET'])
def login():
    data = request.form
    
    if not data or not data.get('user_name') or not data.get('password'):
        return make_response(
            jsonify({"status" : "Feilds missing"}),
            401)
        
    user_name = data.get('user_name')
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
def user_insert():
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
            200
            )


# # gathering entry 
# @app.route("/user/entry" , methods = ["POST" , "GET"])
# def entry():
    
#     data = request.form

#     record = Entry(data["user_name"] , date.today() , datetime.datetime.utcnow())
#     db.session.add(record)
#     db.session.commit()
#     return make_response(
#             jsonify({"status" : "Successfully Updated"}),
#             200
#             )

# # mark attendance 
# @app.route("/user/attendance" , methods = ["POST" , "GET"])
# def attendance() :

#     data = request.form
#     record = Entry.query.filter_by(emp_id = data["emp_id"]) and Entry.query.filter_by(date = date.today()).all()
    
#     count = 0 
#     for x in record :
#         count += 1 
    
#     if count == 3 :
#         detail = Attendance(data["emp_id"], date.today(), "present")
#         db.session.add(detail)
#         db.session.commit()
#     else:
#         detail = Attendance(data["emp_id"], date.today(), "absent")
#         db.session.add(detail)
#         db.session.commit()
#     return make_response(
#             jsonify({"status" : "Successfully Updated"}),
#             200
#             )
# */

