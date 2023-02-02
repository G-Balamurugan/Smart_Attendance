from flask import Flask, request, jsonify, render_template ,make_response
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
from  werkzeug.security import generate_password_hash, check_password_hash
import json
import jwt
from models.models import db,User
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:%s@localhost/booking' % quote_plus('bala')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config['SECRET_KEY'] = 'your secret key'
jsondecoder = json.JSONDecoder()


@app.route("/", methods=['POST', 'GET'])
def root():
    print("Welcome Train Booking")
    return make_response(jsonify({'message' : "Welcome To Train Booking"}), 200)


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
        
        print(token)
        token = str.replace(str(token), "Bearer ", "")
        try:
            #token = jsondecoder.decode(token)
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
            print(data)
            
            current_user = User.query.filter_by(public_id = data['public_id']).first()
            
            if current_user.validity == 0:
                return make_response(
                jsonify({'message' : 'User Logged Out..Need to Login'}),
                401)
            print(current_user)
        except Exception as e:
            print(".....!!!!!.... ", e)
            return make_response(
            jsonify({'message' : 'Token is invalid !!'}),
            401)
        
        print(token)
        return  f(current_user, *args, **kwargs)
    return decorated

#   Signup

@app.route("/user/signup", methods = ['POST','GET'])
def user_insert():
    data = request.form
    
    if not data or not data.get('username') or not data.get('password') or not data.get('userType') or not data.get('email') :
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401
            )
    if not data.get('firstName') or not data.get('lastName') or not data.get('dob'):
        return make_response(
            jsonify({"status" : "Fields missing"}),
            401
            )

    password = data.get('password')       
    user_name , email = data.get('username') , data.get('email')
    first_name , last_name = data.get('firstName') , data.get('lastName')
    user_type = data.get('userType')
    dob = data.get('dob')

    birthdate = datetime.strptime(dob , "%Y-%m-%d")
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    print(age)
    
    user = User.query.filter_by(user_name=user_name).first() or  User.query.filter_by(email=email).first()
    if user:
        return make_response(
            jsonify({"status" : "User Already Exists"}),
            401
            )
    
    password= generate_password_hash(data["password"])

    record = User(first_name,last_name,user_name,email,dob,age,user_type,password,0)
    db.session.add(record)
    db.session.commit()
    return make_response(
            jsonify({"status" : "Successfully Created"}),
            200
            )

#   Login

@app.route("/user/login" , methods = ['POST','GET'])
def login():
    data = request.form
    
    if not data or not data.get('username') or not data.get('password'):
        return make_response(
            jsonify({"status" : "Feilds missing"}),
            401
            )
    user_name = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(user_name = user_name).first()
    print(user,type(user))
    if not user:
        return make_response(
            jsonify({"status" : "User not found"}),
            401
            )
    
    if check_password_hash(user.password, password):
        jwt_token = jwt.encode({
            'public_id': user.public_id,
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
