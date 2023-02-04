from flask import Flask, request, jsonify, render_template ,make_response
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from  werkzeug.security import generate_password_hash, check_password_hash
import json
import jwt
import uuid
from models.models import db,Employee,Login
from Duration import Duration
from datetime import date,datetime, timedelta
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:%s@localhost/smart' % quote_plus('bala')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your secret key'

db.init_app(app)


jsondecoder = json.JSONDecoder()


@app.route("/", methods=['POST', 'GET'])
def root():
    return make_response(jsonify({'message' : "Success"}), 200)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        
        if not token:
            return make_response(
            jsonify({'message' : 'Token is missing !!'}),
            401) 
        
        token = str.replace(str(token), "Bearer ", "")
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            current_user = Login.query.filter_by(user_name = data['user_name']).first()
            
            if current_user.validity == 0:
                return make_response(
                jsonify({'message' : 'User Logged Out..Need to Login'}),
                401)
            
        except Exception as e:
            return make_response(
            jsonify({'message' : 'Token is invalid !!'}),
            401)
        
        # print(token)
        return  f(current_user, *args, **kwargs)
    return decorated

#   Login

@app.route("/login_insert" , methods = ['POST','GET'])
def login_insert():
    
    data = request.form
    
    if not data or not data.get('user_name') or not data.get('password'):
        return make_response(
            jsonify({"status" : "Feilds missing"}),
            401)
    
    user_name = data.get('user_name')
    password = data.get('password')
    user = Login.query.filter_by(user_name = user_name).first()
    
    if user:
        return make_response(
            jsonify({"status" : "User Already Exists"}),
            401)        

    password= generate_password_hash(data["password"])

    record = Login(user_name,password,0) 
    db.session.add(record)
    db.session.commit()
    
    return make_response(
            jsonify({"status" : "Successfully Created"}),
            200)    

@app.route("/login" , methods = ['POST','GET'])
def login():
    data = request.form
    
    if not data or not data.get('user_name') or not data.get('password'):
        return make_response(
            jsonify({"status" : "Feilds missing"}),
            401)
        
    user_name = data.get('user_name')
    password = data.get('password')
    
    user = Login.query.filter_by(user_name = user_name).first()
   
    if not user:
        return make_response(
            jsonify({"status" : "User not found"}),
            401)
    
    if check_password_hash(user.password, password):
        jwt_token = jwt.encode({
            'user_name': user.user_name,
            'exp' : datetime.utcnow() + timedelta(minutes = 3000)
            }, app.config['SECRET_KEY'],"HS256")
        
        setattr(user, "validity", 1)
        db.session.commit()
        
        return make_response(
            jsonify({"status" : "Success", "token" : jwt_token}),
            200)
    else:
        return make_response(
            jsonify({"status" : "Wrong password"}),
            401)

#   Logout

@app.route("/logout" , methods=['POST','GET'])
@token_required
def logout(current_user):
    setattr(current_user, "validity", 0)
    db.session.commit()
    return make_response(
        jsonify({'message' : 'Logged Out'}),
        200)

#   Employee_Details

@app.route("/employee_details", methods = ['POST','GET'])
def user_insert():
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
    print(age)
    
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