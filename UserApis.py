from flask import make_response, request, jsonify
from flask_restful import Resource
from firebase_admin import firestore
from bcrypt import gensalt, checkpw, hashpw
from flask_jwt_extended import create_access_token
from pymongo import MongoClient
import json
from jwt import DecodeError
from jwt.exceptions import PyJWTError as DecodeError
from datetime import datetime



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
        # email = request.json['email']
        # password = request.json['password']
        # phoneNumber = request.json['phoneNumber']

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
        degreeName = request.json['degreeName']
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
        DisabilityYN = request.json['DisabilityYN']
        Charan = request.json['Charan']
        Naadi = request.json['Naadi']
        userIdNew= 0
        
        try:
            if UserId == "0":
                query = {"UserEmail": Email}
                projection = {"_id": 0}
                collection = db.get_collection('User')
                data = collection.find_one(query,projection)
                print(Email)
                if data:
                    print("ALETREXISTS")
                    return jsonify({MessageVariable: FailureString, msgVal: "User Already Exists"})
                else:
                    top_user = collection.find().sort('UserId', -1).limit(1)
                    print(top_user)
                    for user in top_user:
                        userIdNew = user['UserId']+1
                        print(user['UserId']+1)
                    hashed_pass = hash_password(UserPassword)
                    print(hashed_pass)
                    current_time = datetime.now()
                    # id = collection.insert_one({"UserEmail":Email,"UserPassword":hashed_pass.decode('utf-8'),"PhoneNumber":PhoneNumber,
                    #                             "LookingFor":LookinFor ,"ChoosingFor":ChoosingFor,"firstName":firstName ,
                    #                             "lastName":lastName,"Address":Address,"CurrentAddress":CurrentAddress,
                    #                             "birthDate":birthDate, "birthTime":birthTime,
                    #                             "BirthPlace":BirthPlace,"Raas":Raas,
                    #                             "Height": Height,"BloodGrp":BloodGrp,"DegDip":DegDip,
                    #                             "Field":Field, "JobBis":JobBis , "IncomeGroup":IncomeGroup,
                    #                             "Eating":Eating,"Gotra":Gotra, "Dosha":Dosha, "Gana":Gana,         
                    #                             "Devak":Devak, "Nakshatra":Nakshatra,"FamilyType":FamilyType,
                    #                             "Siblings":Siblings,"EduSiblings":EduSiblings,
                    #                             "Property":Property, "EduMother":EduMother,"EduFather":EduFather,
                    #                             "MotherFamily":MotherFamily, "FatherFamily":FatherFamily,
                    #                             "selectedEducations":selectedEducations,"degreeName":degreeName,
                    #                             "selectedIncome":selectedIncome,
                    #                             "eatingHabits" : eatingHabits,
                    #                             "expectedGana":expectedGana, "DisabilityYN":DisabilityYN,
                    #                             "Charan":Charan, "Naadi":Naadi,
                    #                             "CreatedDatetime": current_time,
                    #                             "CreatedBy":"User",
                    #                             "IsActive":True,
                    #                             "IsDeleted":False,
                    #                             "UserRole":"2",
                    #                             "UserPaid":False,
                    #                              "UserId": 
                    #                              userIdNew
                    #                             })
                    access_token = create_access_token(identity=Email)            
                    userData = {
                        "UserId":userIdNew,
                        "firstName" :firstName,
                        "access_token" : access_token,
                        "UserPaid": False,
                        "IsActive": True,
                        "UserRole":2
                        }
                    return jsonify({MessageVariable:SuccessString,"data" : userData})
        except ValueError as e:
            print(f"Error checking password: {e}")
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"AddNewUser-UserApi.py","Exception":e,"Time":datetime.datetime.now,"UserEmail":Email})
            return jsonify({MessageVariable: FailureString, msgVal: "Something Went Wrong"})
        
   

class FetchAllUsers(Resource):
    def post(self):
        filters = request.json['filters']
        isPaidUser = request.json["isPaid"]
        page = request.json['pageNumber']
        rowsPerPage = request.json['rowsPerPage']
        if isPaidUser:
            projection = {"_id": 0,"UserPassword":0}
        else:
            projection = {"_id": 0,"UserPassword":0,"UserEmail":0,"PhoneNumber":0}
        finaldataList = []
        priorDataList = []
        try:
            collection = db.get_collection('User')
            data = collection.find(filters,projection)
            for u in data:
                print(u)
                print('____________________________')
                birth_time = datetime.fromisoformat((u['birthTime']))
                time_only = birth_time.time()
                top_data = {"Name":u['firstName'] + ' ' + u["lastName"],
                    "Address" :  u['Address'] +',' + u["CurrentAddress"],
                    "Education" : u["DegDip"] + ',' + u['Field'],
                    "Income" : u["JobBis"] + ", earns " + u['IncomeGroup'],
                    "Userid" : u['UserId']
                 }
                next_Data = {
                    "Birthdate": datetime.fromisoformat((u['birthDate']).rstrip("Z")).date(),
                    "Birthtime":  str(time_only),
                    "BirthPlace" : u['BirthPlace'],
                    "Bloodgroup" : u["BloodGrp"]

                }
                dictt = {"topData": top_data, "next_data": [next_Data]}
                #next_Data.add
                finaldataList.append(dictt)
                
            return jsonify({MessageVariable:SuccessString,"users": finaldataList})
        except ValueError as e:
            print(f"Error checking password: {e}")
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"AddNewUser-UserApi.py","Exception":e,"Time":datetime.datetime.now})
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
