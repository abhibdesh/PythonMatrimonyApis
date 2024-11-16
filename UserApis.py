from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import firestore
from bcrypt import gensalt, checkpw, hashpw
from flask_jwt_extended import create_access_token
from pymongo import MongoClient
import json
from jwt import DecodeError
from jwt.exceptions import PyJWTError as DecodeError
import datetime


with open('./Config/Creds.json') as f:
    config = json.load(f)
    mongoURI = config['uri']
    databse = config['database']
client = MongoClient(mongoURI)
db = client.get_database(databse)
with open('./Config/Strings.json') as g:
    Strings = json.load(g)
    MethodName = Strings['METHOD_NAME']
    ApiName = Strings['API_NAME']
    SuccessString = Strings['SUCCESS_STRING']
    FailureString = Strings['FAILURE_STRING']
    MessageVariable = Strings['MESSAGE_VARIABLE']
    msgVal=Strings['MESSAGE_VALUE']


class UserLogin(Resource):
    def post(self):
        try:
            email = request.json.get('email')
            password = request.json.get('password')
            user_data = ValidateUser(email, password)  
            access_token = create_access_token(identity=email)            
            if user_data:
                return jsonify({MessageVariable: SuccessString, msgVal: user_data, 'accessToken': access_token})
            else:
                return jsonify({MessageVariable: FailureString, msgVal: "Invalid Credentials"})
        except ValueError as e:
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"UserLogin-UserApi.py","Exception":e,"Time":datetime.datetime.now,"UserEmail":email})
            return jsonify({MessageVariable: FailureString, msgVal: "We Apologize For The Inconvenience.Please Try Again Later"})


class AddNewUser(Resource):
    def post(self):
        # Old Data
        email = request.json['email']
        password = request.json['password']
        phoneNumber = request.json['phoneNumber']

        # New Form Data
        UserId = request.json['UserId']
        LookinFor = request.json['LookinFor']
        ChoosingFor = request.json['ChoosingFor']
        UserPassword = request.json['UserPassword']
        firstName = request.json['firstName']
        lastName = request.json['lastName']
        PhoneNumber = request.json['PhoneNumber']
        Email = request.json['Email']
        Address = request.json['Address']
        CurrentAddress = request.json['CurrentAddress']
        birthDate = request.json['birthDate']
        birthTime = request.json['birthTime']
        BirthPlace = request.json['BirthPlace']
        Raas = request.json['Raas']
        Height = request.json['Height']
        BloodGrp = request.json['BloodGrp']
        DegDip = request.json['DegDip']
        Field = request.json['Field']
        JobBis = request.json['JobBis']
        IncomeGroup = request.json['IncomeGroup']
        Eating = request.json['Eating']
        Gotra = request.json['Gotra']
        Dosha = request.json['Dosha']
        Gana = request.json['Gana']
        Devak = request.json['Devak']
        Nakshatra = request.json['Nakshatra']
        FamilyType = request.json['FamilyType']
        Siblings = request.json['Siblings']
        EduSiblings = request.json['EduSiblings']
        Property = request.json['Property']
        EduMother = request.json['EduMother']
        EduFather = request.json['EduFather']
        MotherFamily = request.json['MotherFamily']
        FatherFamily = request.json['FatherFamily']
        selectedEducations = request.json['selectedEducations']
        selectedIncome = request.json['selectedIncome']
        eatingHabits = request.json['eatingHabits']
        expectedGana = request.json['expectedGana']

        try:
            if UserId == "0":
                query = {"UserEmail": email}
                projection = {"_id": 0}
                collection = db.get_collection('User')
                data = collection.find_one(query,projection)

                if data:
                    return jsonify({MessageVariable: FailureString, msgVal: "User Already Exists"})
                else:
                    top_user = collection.find().sort('UserId', -1).limit(1)
                    for user in top_user:
                        print(user['UserId']+1)
                    hashed_pass = hash_password(password)
                    id = collection.insert_one({"UserEmail":email,"UserPassword":
                                                hashed_pass.decode('utf-8'),"PhoneNumber":phoneNumber,
                                                "CreatedDatetime": datetime.datetime.now,
                                                "CreatedBy":"User",
                                                "IsActive":True,
                                                "IsDeleted":False,
                                                "UserRole":"2",
                                                "UserPaid":False,
                                                "UserId": user['UserId'] + 1
                                                })
                    return jsonify({MessageVariable:SuccessString})
            else
                return jsonify({MessageVariable:'SuccessString'})

        except ValueError as e:
            print(f"Error checking password: {e}")
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"AddNewUser-UserApi.py","Exception":e,"Time":datetime.datetime.now,"UserEmail":email,"PhoneNumber":phoneNumber})
            return jsonify({MessageVariable: FailureString, msgVal: "Something Went Wrong"})
        
def ValidateUser(email, password):
    try:
        query = {"UserEmail": email}
        projection = {"_id": 0}
        collection = db.get_collection('User')
        data = collection.find_one(query,projection)
        
        if data and checkpw(password.encode('utf-8'), data["UserPassword"].encode('utf-8')):
            return data 
        else:
            return None
    except ValueError as e:
        print(f"Error checking password: {e}")
        log = collection.insert_one({"Method":"ValidateUser-UserApi.py","Exception":e,"Time":datetime.datetime.now,"UserEmail":email,"PhoneNumber":phoneNumber})
        return None


def hash_password(password):
    hashed_password = hashpw(password.encode('utf-8'), gensalt())
    return hashed_password
