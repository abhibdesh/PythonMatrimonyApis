from flask import Flask, jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource
from bcrypt import gensalt, checkpw, hashpw
from flask_jwt_extended import create_access_token, jwt_required,get_jwt_identity
from pymongo import MongoClient
import json
from jwt import DecodeError
from jwt.exceptions import PyJWTError as DecodeError
from datetime import datetime
import os
import pytz
import random
import base64
from gridfs import GridFS
from bson import ObjectId
import string



local_timezone = pytz.timezone('Asia/Kolkata')  
now_local_tz = datetime.now(local_timezone)


mongoURI = os.getenv('MONGO_URL')
databse = os.getenv('DATABSE')
client = MongoClient(mongoURI)
db = client.get_database(databse)
fs = GridFS(db)


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
            email = request.json.get('userEmail')
            password = request.json.get('password')
            user_data = ValidateUser(email, password)  
            access_token = create_access_token(identity=email) 
            collection = db.get_collection('User')
            print(email)
            print(password)
            if user_data:
                if(user_data["isLoggedIn"] == 1):
                    return jsonify({MessageVariable: FailureString, msgVal: "This Account is Already Logged In On Another Device."})
                if(user_data["IsActive"] == True):
                    profcompper = profileComplete(user_data)
                    collection.update_one({"UserEmail":email},{"$set":
                                                               {
                                                                   "LastLogin": str(now_local_tz),
                                                                   "lastActivity" : str(now_local_tz),
                                                                   "isLoggedIn":1,
                                                                   "access_token":access_token
                                                                   }
                                                                })
                    paymentCollection = db.get_collection("PaymentInfo")
                    col = paymentCollection.find_one({"UserEmail":email})
                    if col:
                        user_data["IsPaymentDone"] = col["IsPaymentDone"]
                        user_data["IsApproved"]= col["IsApproved"]
                        user_data["UserPaid"]= col["UserPaid"]
                        user_data["TotalProfilesView"]= col["TotalProfilesView"]
                        user_data['LimitExhausted']= col["LimitExhausted"]
                        user_data['ProfileCount']= col["ProfileCount"]
                        if col["LimitExhausted"] == False and col["TotalProfilesView"] <= col["ProfileCount"]:
                            user_data["userPaid"] = False
                        else:
                            user_data["userPaid"] + True
                    else:
                        user_data["IsPaymentDone"] = False
                        user_data["IsApproved"]=False
                        user_data["UserPaid"]= False
                        user_data["TotalProfilesView"]= 0
                        user_data['LimitExhausted']= True
                        user_data["userPaid"] = False
                    return jsonify({MessageVariable: SuccessString,"profileCompletePercentage":profcompper, msgVal: user_data, 'accessToken': access_token})
                else:
                    return jsonify({MessageVariable:  FailureString, msgVal: "This Account is Deactivated. Please Contact Support For Reactivation."})

            else:
                return jsonify({MessageVariable: FailureString, msgVal: "Invalid Credentials"})
        except Exception as e:
            print("hfsdshgfshgd")
            collectiona = db.get_collection("ErrorLogs")
            current = datetime.now()
            print("jsgdghsdjf")
            log = collectiona.insert_one({"Method":"UserLogin-UserApi.py","Exception":e,"Time":current,"UserEmail":email})
            print(log)
            return jsonify({MessageVariable: FailureString, msgVal: "We Apologize For The Inconvenience.Please Try Again Later"})


class AddNewUser(Resource):
    def post(self):
        UserId = request.json['UserId']
        # Step 1 
        LookinFor = request.json['LookinFor']
        ChoosingFor = request.json['ChoosingFor']
        UserPassword = request.json['UserPassword']
        firstName = request.json['firstName']
        lastName = request.json['lastName']
        PhoneNumber = request.json['PhoneNumber']
        Email = request.json['Email']
        Address = request.json['Address']
        CurrentAddress = request.json['CurrentAddress']
        ReferenceCode = request.json["ReferenceCode"]
        # birthDate = request.json['birthDate']
        # birthTime = request.json['birthTime']
        BirthPlace = request.json['BirthPlace']
        Raas = request.json['Raas']
        Height = request.json['Height']
        BloodGrp = request.json['BloodGrp']
        DisabilityYN = request.json['DisabilityYN']
        Disablity = request.json['Disablity']
        # Step 2
        DegDip = request.json['DegDip']
        Field = request.json['Field']
        image = request.json['image']
        degreeName = request.json['degreeName']
        CompanyName = request.json['CompanyName']
        JobBis = request.json['JobBis']
        IncomeGroup = request.json['IncomeGroup']
        Eating = request.json['Eating']
        Gotra = request.json['Gotra']
        Dosha = request.json['Dosha']
        Gana = request.json['Gana']
        Devak = request.json['Devak']
        Nakshatra = request.json['Nakshatra']
        Charan = request.json['Charan']
        Naadi = request.json['Naadi']
        #Step 3
        FamilyType = request.json['FamilyType']
        Siblings = request.json['Siblings']
        EduSiblings = request.json['EduSiblings']
        Property = request.json['Property']
        EduMother = request.json['EduMother']
        EduFather = request.json['EduFather']
        MotherFamily = request.json['MotherFamily']
        FatherFamily = request.json['FatherFamily']
        #Step 4
        selectedIncome = request.json['selectedIncome']
        eatingHabits = request.json['eatingHabits']
        expectedGana = request.json['expectedGana']     
        selectedEducations = request.json['selectedEducations']
        expectedNakshatra = request.json['expectedNakshatra']
        expectedAgeGap = request.json['expectedAgeGap']
        strictMatch = request.json['strictMatch']
        selectedLocatities = request.json['selectedLocatities']
        readTCP = request.json['readTCP']
        userIdNew= 0
        try:
            if UserId == "0":
                query = {"UserEmail": Email}
                # query = {"$or":[ {"UserEmail":Email}, {"PhoneNumber":PhoneNumber}]}
                projection = {"_id": 0}
                collection = db.get_collection('User')
                data = collection.find_one(query,projection)
                print(data)
                if data:
                    print("User Already Exists")
                    return jsonify({MessageVariable: FailureString, msgVal: "User Already Exists"})
                else:
                    top_user = collection.find().sort('UserId', -1).limit(1)
                    print(top_user)
                    for user in top_user:
                        userIdNew = user['UserId']+1
                        print(user['UserId']+1)
                    hashed_pass = hash_password(UserPassword)
                    current_time = datetime.now()
                    # print(birthTime)
                    # date_object = datetime.strptime(birthTime[:24], "%a %b %d %Y %H:%M:%S")
                    # time = date_object.time()
                    # print(time)  
                    access_token = create_access_token(identity=Email) 
                    # birth_date = datetime.fromisoformat(birthDate)
                    # birth_date_only = birth_date.date()
                    today = datetime.today().date()
                    # age = today.year - birth_date_only.year - ((today.month, today.day) 
                    #                                            < (birth_date_only.month,
                    #                                                birth_date_only.day))
                    if Height =='':
                        Height=0
                    else:
                        Height = float(Height)
                    if Siblings =='':
                        Siblings =0
                    id = collection.insert_one({"UserEmail":Email,
                                                "UserPassword":hashed_pass.decode('utf-8'),
                                                "PhoneNumber":PhoneNumber,
                                                "LookingFor":LookinFor ,
                                                "ChoosingFor":ChoosingFor,
                                                "firstName":firstName ,
                                                "lastName":lastName,
                                                "ReferenceCode":ReferenceCode,
                                                "Address":Address,
                                                "CurrentAddress":CurrentAddress,
                                                "isPhoneVerified":False,
                                                "isEmailVerified":False,
                                                "birthDate":None,
                                                "birthTime":None,
                                                "age":None,
                                                "BirthPlace":BirthPlace,
                                                "Raas":Raas,
                                                "Height": Height,
                                                "BloodGrp":BloodGrp,
                                                "Disablity":Disablity,
                                                "DegDip":DegDip,
                                                "Field":Field, 
                                                "JobBis":JobBis , 
                                                "IncomeGroup":IncomeGroup,
                                                "Eating":Eating,
                                                "Gotra":Gotra, 
                                                "Dosha":Dosha, 
                                                "Gana":Gana,         
                                                "Devak":Devak, 
                                                "Nakshatra":Nakshatra,
                                                "FamilyType":FamilyType,
                                                "Siblings":Siblings,
                                                "EduSiblings":EduSiblings,
                                                "Property":Property, 
                                                "EduMother":EduMother,
                                                "EduFather":EduFather,
                                                "MotherFamily":MotherFamily, 
                                                "FatherFamily":FatherFamily,
                                                "selectedEducations":selectedEducations,
                                                "degreeName":degreeName,
                                                "selectedIncome":selectedIncome,
                                                "eatingHabits" : eatingHabits,
                                                "CompanyName":CompanyName,
                                                "expectedGana":expectedGana, 
                                                "DisabilityYN":DisabilityYN,
                                                "Charan":Charan, "Naadi":Naadi,
                                                "CreatedDatetime": str(now_local_tz),
                                                "lastActivity": str(now_local_tz),
                                                "selectedLocatities":selectedLocatities,
                                                "LastLogin":str(now_local_tz),
                                                "lastLogOutTime": None,
                                                "isLoggedIn":1,
                                                "expectedNakshatra":expectedNakshatra,
                                                "strictMatch":True,
                                                "CreatedBy":"User",
                                                "IsActive":True,
                                                "IsDeleted":False,
                                                "UserRole":"2",
                                                "UserPaid":False,
                                                "IsVerified":"0",
                                                 "UserId": 
                                                 userIdNew,
                                                 "image":[],
                                                 "readTCP":readTCP,
                                                 "expectedAgeGapMin": 0,
                                                 "expectedAgeGapMax": 0,
                                                 "selectedBloodGroups":[],
                                                 "selectedNaadi":[],
                                                 "selectedRaas":[],
                                                 "selectedHeight":[],
                                                 "selectedFamilyType":[],
                                                 "selectedSiblingsCousinsUpto":[],
                                                 "strictMatch": True,
                                                 "profileWithImages": False,
                                                 "isLoggedIn":1,
                                                 "access_token":access_token,
                                                 "Community":"",
                                                 "images" :[]
                                                 
                                                })
                    
                    userData = {
                        "UserId":userIdNew,
                        "firstName" :firstName,
                        "access_token" : access_token,
                        "UserPaid": False,
                        "IsActive": True,
                        "UserRole":2,
                        "isPhoneVerified":False,
                        "isEmailVerified":False,
                        }
                    print(userData)
                    return jsonify({MessageVariable:SuccessString,"data" : userData})
        except ValueError as e:
            print(f"Error checking password: {e}")
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"AddNewUser-UserApi.py","Exception":e,"Time":datetime.now,"UserEmail":Email})
            return jsonify({MessageVariable: FailureString, msgVal: "Something Went Wrong"})
        

class UpdateProfile(Resource):
    @jwt_required()
    def post(self):
        # print("Request Headers:", request.headers)
        current_user = get_jwt_identity()
        print("Authenticated User:", current_user)
        UserId = request.json['UserId']
        # Step 1 
        LookinFor = request.json['LookinFor']
        ChoosingFor = request.json['ChoosingFor']
        firstName = request.json['firstName']
        lastName = request.json['lastName']
        PhoneNumber = request.json['PhoneNumber']
        Email = request.json['Email']
        Address = request.json['Address']
        CurrentAddress = request.json['CurrentAddress']
        birthDate = request.json.get("birthDate",None)
        birthTime = request.json.get("birthTime",None)
        # birthTime = request.json['birthTime']
        BirthPlace = request.json['BirthPlace']
        Raas = request.json['Raas']
        Height = request.json['Height']
        BloodGrp = request.json['BloodGrp']
        DisabilityYN = request.json['DisabilityYN']
        Disablity = request.json['Disablity']
        # Step 2
        DegDip = request.json['DegDip']
        Field = request.json['Field']
        image = request.json['image']
        degreeName = request.json['degreeName']
        CompanyName = request.json['CompanyName']
        JobBis = request.json['JobBis']
        IncomeGroup = request.json['IncomeGroup']
        Eating = request.json['Eating']
        Gotra = request.json['Gotra']
        Dosha = request.json['Dosha']
        Gana = request.json['Gana']
        Devak = request.json['Devak']
        Nakshatra = request.json['Nakshatra']
        Charan = request.json['Charan']
        Naadi = request.json['Naadi']
        #Step 3
        FamilyType = request.json['FamilyType']
        Siblings = request.json['Siblings']
        EduSiblings = request.json['EduSiblings']
        Property = request.json['Property']
        EduMother = request.json['EduMother']
        EduFather = request.json['EduFather']
        MotherFamily = request.json['MotherFamily']
        FatherFamily = request.json['FatherFamily']        
        try:
            print(strictMatch)
            print("birthDate")
            print(birthDate)
            print("__________________________________")
            print("birthTime")
            print(birthTime)
            print("*********************************")
            
            if(birthDate != None and birthTime != None ):
                # BIRTH DATE SECTION
                print("BOTH AVAILABLE")
                
                # date_obj = datetime.strptime(birthDate, "%a, %d %b %Y %H:%M:%S %Z")
                # date_obj = datetime.strptime(birthDate, '%Y-%m-%dT%H:%M:%S.%fZ')
                # date_obj = datetime.strptime(birthDate, '%a, %d %b %Y %H:%M:%S %Z')
                date_obj = parse_birth_date(birthDate)
                print(date_obj)
                birth_date_only = date_obj.date()
                today = datetime.today().date()
                age = today.year - birth_date_only.year - ((today.month, today.day) 
                                                               < (birth_date_only.month,
                                                                   birth_date_only.day))
                # BIRTH TIME SECTION
                print(birthTime)
                date_object = datetime.strptime(birthTime[:24], "%H:%M:%S")
                time = date_object.time()
                print(time)  
                # HAS BIRTH DATE AND TIME
                newData = {
                        "UserEmail":Email,
                        "PhoneNumber":PhoneNumber,
                        "LookingFor":LookinFor ,
                        "ChoosingFor":ChoosingFor,
                        "firstName":firstName ,
                        "lastName":lastName,
                        "Address":Address,
                        "lastActivity":str(now_local_tz),
                        "CurrentAddress":CurrentAddress,
                        "birthDate":date_obj,
                        "birthTime":time.strftime("%H:%M:%S"),
                        "age":age,
                        "BirthPlace":BirthPlace,"Raas":Raas,
                        "Height": float(Height),
                        "BloodGrp":BloodGrp,
                        "Disablity":Disablity,
                        "DegDip":DegDip,
                        "Field":Field, 
                        "JobBis":JobBis , 
                        "IncomeGroup":IncomeGroup,
                        "Eating":Eating,
                        "Gotra":Gotra, 
                        "Dosha":Dosha, 
                        "Gana":Gana,         
                        "Devak":Devak, 
                        "Nakshatra":Nakshatra,
                        "FamilyType":FamilyType,
                        "Siblings":Siblings,
                        "EduSiblings":EduSiblings,
                        "Property":Property, 
                        "EduMother":EduMother,
                        "EduFather":EduFather,
                        "MotherFamily":MotherFamily, 
                        "FatherFamily":FatherFamily,
                        "degreeName":degreeName,
                        "CompanyName":CompanyName,
                        "DisabilityYN":DisabilityYN,
                        "Charan":Charan, 
                        "Naadi":Naadi,
                        "CreatedBy":"User",
                        "IsActive":True,
                        "IsDeleted":False,
                        "image":image
                        }
            if(birthDate == None and birthTime != None):
                print("ONLY BIRTHTIME")

                print(birthTime)
                date_object = datetime.strptime(birthTime[:24], "%H:%M:%S")
                time = date_object.time()
                print(time)  
                newData = {
                        "UserEmail":Email,
                        "PhoneNumber":PhoneNumber,
                        "LookingFor":LookinFor ,
                        "ChoosingFor":ChoosingFor,
                        "firstName":firstName ,
                        "lastName":lastName,
                        "lastActivity":str(now_local_tz),
                        "birthTime":time.strftime("%H:%M:%S"),
                        "Address":Address,
                        "CurrentAddress":CurrentAddress,
                        "BirthPlace":BirthPlace,"Raas":Raas,
                        "Height": float(Height),
                        "BloodGrp":BloodGrp,
                        "Disablity":Disablity,
                        "DegDip":DegDip,
                        "Field":Field, 
                        "JobBis":JobBis , 
                        "IncomeGroup":IncomeGroup,
                        "Eating":Eating,
                        "Gotra":Gotra, 
                        "Dosha":Dosha, 
                        "Gana":Gana,         
                        "Devak":Devak, 
                        "Nakshatra":Nakshatra,
                        "FamilyType":FamilyType,
                        "Siblings":Siblings,
                        "EduSiblings":EduSiblings,
                        "Property":Property, 
                        "EduMother":EduMother,
                        "EduFather":EduFather,
                        "MotherFamily":MotherFamily, 
                        "FatherFamily":FatherFamily,
                        "degreeName":degreeName,
                        "CompanyName":CompanyName,
                        "DisabilityYN":DisabilityYN,
                        "Charan":Charan, "Naadi":Naadi,
                        "CreatedBy":"User",
                        "IsActive":True,
                        "IsDeleted":False,
                        "image":image
                        }

            if(birthDate != None and birthTime == None):
                # BIRTH DATE SECTION
                print("ONLY BITHDATE")
                # date_obj = datetime.strptime(birthDate, '%a, %d %b %Y %H:%M:%S %Z')
                date_obj = parse_birth_date(birthDate)
                print(date_obj)
                birth_date_only = date_obj.date()
                today = datetime.today().date()
                age = today.year - birth_date_only.year - ((today.month, today.day) 
                                                               < (birth_date_only.month,
                                                                   birth_date_only.day))
                newData = {
                    "UserEmail":Email,
                    "PhoneNumber":PhoneNumber,
                    "LookingFor":LookinFor ,
                    "ChoosingFor":ChoosingFor,
                    "firstName":firstName ,
                    "lastName":lastName,
                    "Address":Address,
                    "lastActivity":str(now_local_tz),
                    "CurrentAddress":CurrentAddress,
                    "birthDate":date_obj,
                    "age":age,
                    "BirthPlace":BirthPlace,"Raas":Raas,
                    "Height": float(Height),
                    "BloodGrp":BloodGrp,
                    "Disablity":Disablity,
                    "DegDip":DegDip,
                    "Field":Field, 
                    "JobBis":JobBis , 
                    "IncomeGroup":IncomeGroup,
                    "Eating":Eating,
                    "Gotra":Gotra, 
                    "Dosha":Dosha, 
                    "Gana":Gana,         
                    "Devak":Devak, 
                    "Nakshatra":Nakshatra,
                    "FamilyType":FamilyType,
                    "Siblings":Siblings,
                    "EduSiblings":EduSiblings,
                    "Property":Property, 
                    "EduMother":EduMother,
                    "EduFather":EduFather,
                    "MotherFamily":MotherFamily, 
                    "FatherFamily":FatherFamily,
                    "degreeName":degreeName,
                    "CompanyName":CompanyName,
                    "DisabilityYN":DisabilityYN,
                    "Charan":Charan, "Naadi":Naadi,
                    "CreatedBy":"User",
                    "IsActive":True,
                    "IsDeleted":False,
                    "image":image
                        }

            if(birthTime == None and birthDate == None):
                print("BOTH UNAVAILABLE")

                newData = {
                        "UserEmail":Email,
                        "PhoneNumber":PhoneNumber,
                        "LookingFor":LookinFor ,
                        "ChoosingFor":ChoosingFor,
                        "firstName":firstName ,
                        "lastName":lastName,
                        "Address":Address,
                        "BirthPlace":BirthPlace,"Raas":Raas,
                        "Height": float(Height),
                        "BloodGrp":BloodGrp,
                        "lastActivity":str(now_local_tz),
                        "Disablity":Disablity,
                        "DegDip":DegDip,
                        "Field":Field, 
                        "JobBis":JobBis , 
                        "IncomeGroup":IncomeGroup,
                        "Eating":Eating,
                        "Gotra":Gotra, 
                        "Dosha":Dosha, 
                        "Gana":Gana,         
                        "Devak":Devak, 
                        "Nakshatra":Nakshatra,
                        "FamilyType":FamilyType,
                        "Siblings":Siblings,
                        "EduSiblings":EduSiblings,
                        "Property":Property, 
                        "EduMother":EduMother,
                        "EduFather":EduFather,
                        "MotherFamily":MotherFamily, 
                        "FatherFamily":FatherFamily,
                        "degreeName":degreeName,
                        "CompanyName":CompanyName,
                        "expectedGana":expectedGana, 
                        "Charan":Charan, "Naadi":Naadi,
                        "CreatedBy":"User",
                        "IsActive":True,
                        "IsDeleted":False,
                        "image":image
                        }

            if Height =='':
                Height = 0
            else:
                Height = float(Height)
            if Siblings =='':
                Siblings = 0
            else:
                Height = float(Height)
           
            collection = db.get_collection('User')
            data = collection.find_one({"UserId":int(UserId)})
            
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            else:
                collection.update_one({"UserEmail":get_jwt_identity()},{"$set":{"lastActivity":str(now_local_tz)}})
                collection.update_one({"UserId":int(UserId)},{"$set":newData})
                d = collection.find_one({"UserId":int(UserId)})
                profileUpdate = profileComplete(d)
                return jsonify({"message": "Success","data":"Profile Updated Successfully","profileUpdate":profileUpdate,"image":d['image']})

        except Exception as e:
            print("Error:", e)
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"UpdateProfile-UserApi.py","Exception":str(e),"Time":datetime.now})
            return jsonify({"message": "An error occurred during logout", "error": str(e)})

        
class UpdatePreferences(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        print("Authenticated User:", current_user)
        UserId = request.json['UserId']
        selectedIncome = request.json['selectedIncome']
        eatingHabits = request.json['eatingHabits']
        expectedGana = request.json['expectedGana']     
        selectedEducations = request.json['selectedEducations']
        expectedNakshatra = request.json['expectedNakshatra']
        selectedLocatities = request.json['selectedLocatities']  
        expectedAgeGapMin = request.json['expectedAgeGapMin']  
        expectedAgeGapMax = request.json['expectedAgeGapMax']  
        selectedBloodGroups = request.json['selectedBloodGroups']  
        selectedNaadi = request.json['selectedNaadi']  
        selectedRaas = request.json['selectedRaas']  
        selectedHeight = request.json['selectedHeight']  
        selectedFamilyType = request.json['selectedFamilyType']  
        selectedSiblingsCousinsUpto = request.json['selectedSiblingsCousinsUpto']  
        strictMatch = request.json['strictMatch']  
        profileWithImages = request.json['profileWithImages']

        try:
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            else:
                collection = db.get_collection('User')
                data = collection.find_one({"UserEmail":current_user})
                newdata = {
                    
                }
                collection.update_one({"UserEmail":get_jwt_identity()},{"$set":{
"lastActivity":str(now_local_tz),
                    "selectedIncome":selectedIncome,
                    "eatingHabits":eatingHabits,
                    "expectedGana":expectedGana,
                    "selectedEducations":selectedEducations,
                    "expectedNakshatra":expectedNakshatra,
                    "strictMatch":strictMatch,
                    "selectedLocatities":selectedLocatities,
                    "expectedAgeGapMin": float(expectedAgeGapMin) if expectedAgeGapMin !="" else "" ,
                    "expectedAgeGapMax":float(expectedAgeGapMax) if expectedAgeGapMax !="" else "",
                    "selectedBloodGroups":selectedBloodGroups,
                    "selectedNaadi":selectedNaadi,
                    "selectedRaas":selectedRaas,
                    "selectedHeight":float(selectedHeight) if selectedHeight !="" else "",
                    "selectedFamilyType":selectedFamilyType,
                    "selectedSiblingsCousinsUpto":selectedSiblingsCousinsUpto,
                    "profileWithImages":profileWithImages,
                }})
                return jsonify({"message":"Success","data":"Preferences Updated Successfully!"})

        except Exception as e:
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"UpdatePreferences-UserApi.py","Exception":e,"Time":datetime.now})
            return jsonify({MessageVariable: FailureString, msgVal: "Something Went Wrong"})
            
        
        
                
class GetSingleProfileData(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        print("Authenticated User:", current_user)
        userId = request.json["UserId"]
        try:           
            newFilter = {"UserId" : int(userId)}            
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            else:
                collection = db.get_collection('User')
                paymentCollection = db.get_collection("PaymentInfo")
                paymnetInfo = paymentCollection.find_one(
                {"UserEmail": current_user},
                sort=[("CreatedDate", -1)])
                collection.update_one({"UserEmail":current_user},{"$set":{"lastActivity":str(now_local_tz)}})
                curr_user =  collection.find_one({"UserEmail":current_user})
                projection = {"_id": 0,"UserPassword":0,"CreatedDatetime":0,"LastLogin":0,"CreatedBy":0,
                            "IsActive":0, "IsDeleted":0, "UserRole":0, "UserPaid":0}
            
                data = collection.find_one(newFilter,projection)
                final_data = {}
                # Introduction Section
                if data["birthDate"] == None:
                    day_name = ""
                else:
                    day_name = data["birthDate"].date().strftime("%A") if data["birthDate"] is not None else "NA"
                final_data["image"] = data["image"] if data["image"] is not None else ""
                final_data["Name"] = data["firstName"]+" " + data["lastName"]
                # Contact Details

                emailIdString = "Buy Our Services For Contact Information"
                contactNumberString = "Buy Our Services For Contact Information"
                paymentplan = "None"
                if paymnetInfo is not None:
                    print(paymnetInfo["savedProfiles"])
                    print(data["UserId"])
                    if(data["UserId"] in paymnetInfo["savedProfiles"]):
                        final_data["isAlreadyAdded"] = True
                    else:
                        final_data["isAlreadyAdded"] = False
                    if paymnetInfo["IsApproved"] == 1 and (len(paymnetInfo["savedProfiles"]) < paymnetInfo["ProfileCount"] or paymnetInfo["ProfileCount"]==0) and  paymnetInfo["ValidTill"] > datetime.now():
                        paymentplan = "Active"
                    if int(userId) in paymnetInfo["savedProfiles"] and paymnetInfo["IsApproved"] == 1 and paymnetInfo["ValidTill"] > datetime.now():
                        emailIdString = data["UserEmail"]
                        contactNumberString = data["PhoneNumber"]
                        
                       
                    if data["isEmailVerified"] == True:
                        emailIdString = data["UserEmail"]
                    else:
                        emailIdString  = "Unverified Email" 
                    
                    if data["isPhoneVerified"] == True:
                        contactNumberString = data["PhoneNumber"]
                    else:
                        contactNumberString  = "Unverified Phone Number"        
                
                    if curr_user["isEmailVerified"] != True:
                        emailIdString  = "Verify Your Email"  
                    if curr_user["isPhoneVerified"] != True:
                        contactNumberString  = "Verify Your Mobile Number" 
                else:
                    paymentplan = "None"

                final_data["PhoneNumber"] = contactNumberString
                final_data["UserEmail"] = emailIdString
                final_data["Community"] = data["Community"]      
                if(data["ReferenceCode"]!=""):
                    admindata = collection.find_one({"UserRole":"3","ReferenceCode":data["ReferenceCode"]})
                    final_data["ReferenceName"] = admindata["firstName"] + " " + admindata["lastName"]
                else:
                    final_data["ReferenceName"] = "NA"
                final_data["JobBis"]= data["JobBis"] if  data["JobBis"] != "" else "Not Provided"
                final_data["DegDip"]= data["DegDip"] if data["DegDip"] !="" else "Not Provided"
                final_data["FieldOrPost"]= data["Field"] if data["Field"] !="" else "Not Provided"
                final_data["DegreeName"]= data["degreeName"] if data["degreeName"] !="" else "Not Provided"
                final_data["CompanyName"]= data["CompanyName"] if data["CompanyName"] !="" else "Not Provided"
                final_data["IncomeGroup"]= data["IncomeGroup"] if data["IncomeGroup"] !="" else "Not Provided"
                final_data["CurrentAddress"]= str(data["CurrentAddress"]) if str(data["CurrentAddress"])  else "Not Provided"
                final_data["FullAddress"]= str(data["Address"])+", " + str(data["CurrentAddress"]) if str(data["Address"])+", " + str(data["CurrentAddress"]) != "" else "Not Provided"
                # Mandatory to know for patrika match section
                if data["birthDate"] == None:
                    final_data["BirthDate"]  = "Not Provided"
                else:
                    date_obj4 = data["birthDate"]
                    formatted_date = date_obj4.strftime("%d %B %Y")
                    day_name = date_obj4.strftime("%A")  
                    final_data["BirthDate"] = f"{formatted_date}, {day_name}"
                 
                if data["birthTime"] == None:
                    final_data["birthTime"]  = "Not Provided"
                else:
                    time_obj = datetime.strptime(data["birthTime"], "%H:%M:%S")
                    formatted_time = time_obj.strftime("%I:%M %p")  # e.g., "05:44 AM"
                    final_data["BirthTime"] = formatted_time
                    # final_data["BirthTime"]= data["birthTime"] + " (24 Hour Format)" if data["birthTime"] is not None else "Not Provided"
                final_data["BirthPlace"]= data["BirthPlace"]
                final_data["Height"]= str(str(data["Height"]) + " Feet") if str(str(data["Height"]) + " Feet") != " Feet" else "Not Provided"
                final_data["BloodGroup"]= str(data["BloodGrp"]) if  str(data["BloodGrp"]) !="" else "Not Provided"
                final_data["Naadi"]= str(data["Naadi"]) if str(data["Naadi"]) != "" else "Not Provided"
                final_data["Disablity"]= str(data["Disablity"])  if str(data["Disablity"]) != "" else "Not Applicable"
                final_data["Raas"]= str(data["Raas"]) if str(data["Raas"])   != "" else "Not Provided"
                final_data["Devak"]= str(data["Devak"]) if str(data["Devak"])   != "" else "Not Provided"
                final_data["Gotra"]= str(data["Gotra"]) if str(data["Gotra"])  != "" else "Not Provided"
                final_data["Gana"]= str(data["Gana"]) if str(data["Gana"])   != "" else "Not Provided"
                final_data["Charan"]= str(data["Charan"]) if str(data["Charan"])   != "" else "Not Provided"
                final_data["Nakshatra"]= str(data["Nakshatra"]) if str(data["Nakshatra"])   != "" else "Not Provided"
                # Family Details Section
                final_data["FamilyType"]= str(data["FamilyType"]) if str(data["FamilyType"])    != "" else "Not Provided"
                final_data["Siblings"]= str(data["Siblings"]) if str(data["Siblings"])    != "0" else "None"
                final_data["EduSiblings"]= str(data["EduSiblings"])  if  str(data["EduSiblings"])  != "" else "Not Provided"
                final_data["Property"]= str(data["Property"]) if str(data["Property"])    != "" else "Not Provided"
                final_data["EduMother"]= str(data["EduMother"]) if str(data["EduMother"])    != "" else "Not Provided"
                final_data["EduFather"]= str(data["EduFather"]) if str(data["EduFather"])    != "" else "Not Provided"
                final_data["MotherFamily"]= str(data["MotherFamily"]) if str(data["MotherFamily"])   != "" else "Not Provided"
                final_data["FatherFamily"]= str(data["FatherFamily"]) if str(data["FatherFamily"])    != "" else "Not Provided"
                # Expectations Section
                final_data["selectedEducations"]= ", ".join(data["selectedEducations"]) if ", ".join(data["selectedEducations"]) != "" else "No bar"
                final_data["selectedIncome"]= ", ".join(data["selectedIncome"]) if ", ".join(data["selectedIncome"])  != "" else "No bar"
                final_data["eatingHabits"]= ", ".join(data["eatingHabits"]) if ", ".join(data["eatingHabits"])  != "" else "No bar"
                final_data["expectedGana"]= ", ".join(data["expectedGana"]) if ", ".join(data["expectedGana"])  != "" else "No bar"
                final_data["selectedLocatities"]= ", ".join(data["selectedLocatities"]) if ", ".join(data["selectedLocatities"])  != "" else "No bar"
                final_data["expectedNakshatra"]= ", ".join(data["expectedNakshatra"]) if ", ".join(data["expectedNakshatra"])  != "" else "No bar"
                final_data["selectedBloodGroups"]= ", ".join(data["selectedBloodGroups"]) if ", ".join(data["selectedBloodGroups"])  != "" else "No bar"
                final_data["selectedNaadi"]= ", ".join(data["selectedNaadi"]) if ", ".join(data["selectedNaadi"])  != "" else "No bar"
                final_data["selectedRaas"]= ", ".join(data["selectedRaas"]) if ", ".join(data["selectedRaas"])  != "" else "No bar"
                final_data["selectedHeight"]= data["selectedHeight"] if data["selectedHeight"] != "" else "No bar"
                final_data["selectedFamilyType"]= ", ".join(data["selectedFamilyType"]) if ", ".join(data["selectedFamilyType"])  != "" else "No bar"
                final_data["selectedSiblingsCousinsUpto"]= data["selectedSiblingsCousinsUpto"] if (data["selectedSiblingsCousinsUpto"])  != "" else "No bar"
                final_data["expectedAgeGap"]= str(data["expectedAgeGapMin"]) + "-"  + str(data["expectedAgeGapMax"]) if str(data["expectedAgeGapMin"])  != "0" and str(data["expectedAgeGapMax"]) != "0" else "No bar"
                final_data["expectedAgeGapMax"]= str(int(data["expectedAgeGapMax"])) + " years" if(data["expectedAgeGapMax"]!="") else "No bar"
                final_data["expectedAgeGapMin"]= str(int(data["expectedAgeGapMin"]))  + " years" if(data["expectedAgeGapMin"]!="") else "No bar"
                final_data["strictMatch"]= "Yes" if data["strictMatch"] == True else "No" 
                final_data["IsVerified"] = "1" if data["IsVerified"] == "1" else "0" 
                final_data["paymentplan"] = paymentplan
                media=[]    
                if(len(data["images"]) > 0) :  
                    files = list(db.fs.files.find({ "metadata.UserEmail":data["UserEmail"] }))
                    for file in files:
                        chunks_cursor = db.fs.chunks.find({ "files_id": file["_id"] }).sort("n", 1)
                        base64_chunks = [base64.b64encode(chunk["data"]).decode("utf-8") for chunk in chunks_cursor]
                        media.append({
                            "fileId":  str(file["_id"]),
                            "filename": file.get("filename", ""),
                            "contentType": file.get("contentType", "image/jpeg"),
                            "length": file.get("length", 0),
                            "chunks": base64_chunks,
                        })        
                    
                final_data["image"] = media
                final_data["isVerified"] = data["IsVerified"]
            return jsonify({MessageVariable:SuccessString,"data":final_data})
        except Exception as e:
            print(e)
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"GetSingleProfileData-UserApi.py","Exception":e,"Time":datetime.now})
            return jsonify({MessageVariable: FailureString, msgVal: "Something Went Wrong"})


class LogOutFromPreviousDevice(Resource):
    def post(self):
        userEmail = request.json["userEmail"]
        password = request.json["password"]
        collection = db.get_collection("User")
        user_data = ValidateUser(userEmail, password)  
        if user_data:
            collection.update_one({"UserEmail":userEmail},{
                    "$set":{
                        "lastActivity":str(now_local_tz),
                        "lastLogOutTime":str(now_local_tz),
                        "isLoggedIn":0
                        }
                })
            return jsonify({"message":"Success","data":"User Logged Out Successfully"})

        else:
            return jsonify({"message":"Failure","data":"Invalid Credentials"})


class LogoutUser(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            print("Authenticated User:", current_user)
            collection = db.get_collection("User")
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            else:
                collection.update_one({"UserEmail":current_user},{
                    "$set":{
                        "lastActivity":str(now_local_tz),
                        "lastLogOutTime":str(now_local_tz),
                        "isLoggedIn":0,
                        "access_token":None
                        }
                })
                return jsonify({MessageVariable: "Done"})
        except Exception as e:
            print("Error:", e)
            return jsonify({"message": "An error occurred during logout", "error": str(e)}), 500


class FetchMyProfile(Resource):
    @jwt_required()
    def post(self):
        userid = request.json["UserId"]
        current_user = get_jwt_identity()
        try:
            projection = {"_id": 0,"UserPassword":0}
            newFilter = {"UserId" : int(userid)}
            print(newFilter)
            collection = db.get_collection('User')
            data = collection.find_one({"UserEmail":current_user})
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            else:
                collection.update_one(newFilter,{
                    "$set":{
                        "lastActivity":str(now_local_tz),
                        }
                })
                data = collection.find(newFilter,projection)
                myProfile = []
                for u in data:
                    myProfile.append(u)
                return jsonify({MessageVariable:SuccessString,"data": myProfile})

        except ValueError as e:
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"fetchMyProfile-UserApi.py","Exception":e,"Time":datetime.now})
            return jsonify({MessageVariable: FailureString, msgVal: "Something Went Wrong"})
        


class FetchAllUsers(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        print("USER DASHBOARD")
        # print("Authenticated User:", current_user)
        filters = request.json['filters']
        isPaidUser = request.json["isPaid"]
        page = int(request.json['pageNumber'])
        rowsPerPage = int(request.json['rowsPerPage'])
        Userid = request.json["Userid"]

        projection = {"_id": 0, "UserPassword": 0}
        if not isPaidUser:
            projection.update({"UserEmail": 0, "PhoneNumber": 0})
        finaldataList = []

        # Final Filters List 
        allLocalities =[]
        allIncomes =[]
        allEducations = []

        allBloodGroups = []
        allFamilyTypes = []
        allRaas = []
        allNaadi = []
        selectedHeight = 0
        expectedAgeGapMin = 0
        expectedAgeGapMax = 0
        print(filters)

        try:
            filters["IsDeleted"] = False
            collection = db.get_collection('User')
            print("hagsjdgahsjdgasjdgjashgdjhasgdjhsagdjhgasdjhgasjdghsjdgha")

            currentUser = collection.find_one({"UserId": int(Userid)})
            # print(current_user)
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            if not currentUser:
                return jsonify({"message": "User not found", "users": []})
            
            collection.update_one({"UserId": int(Userid)},{"$set":{"lastActivity":str(now_local_tz)}})
            print("getting new filters")
            newFilter = {"UserId": {"$ne":int(Userid)}
                         ,"UserRole": "2", "IsDeleted": False, "IsActive":True, 
                         "LookingFor": {"$ne": currentUser.get("LookingFor")},"isEmailVerified":True,"isPhoneVerified":True }
            if int(filters["selectedFromHeight"]) > 0 and int(filters["selectedToHeight"]) > 0:
                newFilter["Height"] = {"$gte": float(filters["selectedFromHeight"]),"$lte": float(filters["selectedToHeight"])}
            if filters["expectedAgeGapMin"] is not None :
                newFilter["birthDate"] = {"$gte": datetime(filters["expectedAgeGapMin"], 1, 1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)}
            if filters["expectedAgeGapMax"] is not None :
                newFilter["birthDate"] = {"$lte": datetime(filters["expectedAgeGapMax"], 12, 31, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)}
            if filters["expectedAgeGapMin"] is not None and filters["expectedAgeGapMax"] is not None:
                newFilter["birthDate"] = {"$gte": datetime(filters["expectedAgeGapMin"], 1, 1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None) ,"$lte": datetime(filters["expectedAgeGapMax"], 1, 1, hour=0, minute=0, second=0, microsecond=0, tzinfo=None)}
           

             
            # Checking Incomes
            if len(filters["selectedIncomes"]) > 0:
                for i in filters["selectedIncomes"]:
                    allIncomes.append(i)
            elif len(currentUser["selectedIncome"]) > 0 :
                for i in currentUser["selectedIncome"]:
                    allIncomes.append(i)

            # Checking Localities
            if len(filters["selectedLocatities"]) > 0 :
                for i in filters["selectedLocatities"]:
                    allLocalities.append(i)
            elif(len(currentUser["selectedLocatities"]) > 0):
                for i in currentUser["selectedLocatities"]:
                    allLocalities.append(i)
            
            # Checking Educations
            if len(filters["selectedEducations"]) > 0:
                for i in filters["selectedEducations"]:
                    allEducations.append(i)
            elif len(currentUser["selectedEducations"]) > 0 :
                for i in currentUser["selectedEducations"]:
                    allEducations.append(i)

            # Checking Blood Group
            if len(filters["selectedBloodGroups"]) > 0:
                for i in filters["selectedBloodGroups"]:
                    allBloodGroups.append(i)
            elif len(currentUser["selectedBloodGroups"]) > 0:
                for i in currentUser["selectedBloodGroups"]:
                    allBloodGroups.append(i)

            # Checking Family Type
            if len(filters["FamilyType"]) > 0:
                for i in filters["FamilyType"]:
                    allFamilyTypes.append(i)
            elif len(currentUser["selectedFamilyType"]) > 0:
                print(currentUser["selectedFamilyType"])
                for i in currentUser["selectedFamilyType"]:
                    allFamilyTypes.append(i)

            # Checking Raas
            if len(filters["selectedRaas"]) > 0:
                for i in filters["selectedRaas"]:
                    allRaas.append(i)
            elif len(currentUser["selectedRaas"]) > 0:
                for i in currentUser["selectedRaas"]:
                    allRaas.append(i)


            if len(filters["selectedNaadi"]) > 0:
                for i in filters["selectedNaadi"]:
                    allNaadi.append(i)
            if len(currentUser["selectedNaadi"]) > 0:
                for i in currentUser["selectedNaadi"]:
                    allNaadi.append(i)

            if int(filters["selectedSiblingsCousinsUpto"]) > 0:
                newFilter["Siblings"] = {"$lte": int(filters["selectedSiblingsCousinsUpto"])}
           
            # Making Filters
            if(len(allIncomes) > 0):
                newFilter["IncomeGroup"] = {"$in":allIncomes}
            if(len(allLocalities) > 0):
                newFilter["CurrentAddress"] = {"$in":allLocalities}
            if len(allEducations) > 0 :
                newFilter["DegDip"] = {"$in":allEducations}
            if len(allBloodGroups) > 0:
                newFilter["BloodGrp"] = {"$in":allBloodGroups}
            if len(allFamilyTypes) > 0:
                newFilter["FamilyType"] = {"$in":allFamilyTypes}
            if len(allRaas) > 0 :
                newFilter["Raas"] = {"$in": allRaas}
            if len(allNaadi) > 0:
                newFilter["Naadi"] =  {"$in": allNaadi}
            
            newFilter["Community"] = {"$exists":True,"$ne":""}

            print(newFilter)

            total_count = collection.count_documents(newFilter) 
          
            data = (
                collection.find(newFilter, projection)
                .skip((page - 1) * rowsPerPage) 
                .limit(rowsPerPage)  
            )

            for u in data:
                income = "NA"
                print(u["birthDate"])
                if u["JobBis"] and u['IncomeGroup']:
                    income = u["JobBis"] + ", earns " + u['IncomeGroup']
                media = []
                if(len(u["image"])>0):
                    file_id = ObjectId(u["image"][0])
                    file = db.fs.files.find_one({"_id": file_id})
                    chunks_cursor = db.fs.chunks.find({"files_id": file_id}).sort("n", 1)
                    base64_chunks = [base64.b64encode(chunk["data"]).decode("utf-8") for chunk in chunks_cursor]
                    media.append({
                    "fileId": str(file["_id"]),
                    "filename": file.get("filename", ""),
                    "contentType": file.get("contentType", "image/jpeg"),
                    "length": file.get("length", 0),
                    "chunks": base64_chunks,
                    }) 
                top_data = {
                    "Name": u['firstName'] + ' ' + u["lastName"],
                    "Community":u["Community"],
                    "Address":  str(u["CurrentAddress"]),
                    "Education": str(u["DegDip"]) + ', ' + str(u['Field']),
                    "Income": income,
                    "Userid": u['UserId'],
                    "IsVerified":u["IsVerified"],
                    "image": media ,
                    "Birthdate": u['birthDate'],
                    "Birthtime": u['birthTime'],
                    "BirthPlace": u['BirthPlace'],
                    "Bloodgroup": u["BloodGrp"] 
                }

                finaldataList.append({"topData": top_data})

            return jsonify({
                "message": "Success",
                "users": finaldataList,
                "totalCount": total_count,  
                "currentPage": page,
                "rowsPerPage": rowsPerPage
            })
        except Exception as e:
            print(f"Error fetching users: {e}")
            error_collection = db.get_collection('ErrorLogs')
            error_collection.insert_one({
                "Method": "FetchAllUsers",
                "Exception": str(e),
                "Time": datetime.now()
            })
            return jsonify({"message": "Failure", "error": "Something Went Wrong"})
        
class MySavedProfiles(Resource):
    @jwt_required()
    def post(self):
        data = request.json
        filters = data.get('filters', {})
        is_paid_user = data.get("isPaid", False)
        page = int(data.get('pageNumber', 1))
        rows_per_page = int(data.get('rowsPerPage', 10))
        user_id = int(data.get("Userid"))

        if not checkUserDevice(get_jwt_identity(), request.headers.get("Authorization")):
            return jsonify({"message": "Failure", "data": "Session Timed Out"})

        payment_collection = db.get_collection("PaymentInfo")
        user_collection = db.get_collection("User")

        # Fetch all saved profile IDs
        saved_profiles = payment_collection.find({"UserId": user_id}, {"savedProfiles": 1, "_id": 0})
        users_to_fetch = set()
        for record in saved_profiles:
            users_to_fetch.update(record.get("savedProfiles", []))

        users_to_fetch = list(users_to_fetch)

        if not users_to_fetch:
            return jsonify({
                "message": "Success",
                "users": [],
                "totalCount": 0,
                "currentPage": page,
                "rowsPerPage": rows_per_page
            })

        # Fetch user profiles with pagination
        query = {"UserId": {"$in": users_to_fetch}}
        projection = {"_id": 0, "UserPassword": 0, "access_token": 0}
        cursor = user_collection.find(query, projection).skip((page - 1) * rows_per_page).limit(rows_per_page)
        total_count = user_collection.count_documents(query)

        users = []
        for user in cursor:
            # Construct income string
            job = user.get("JobBis", "")
            income_group = user.get("IncomeGroup", "")
            income = f"{job}, earns {income_group}" if job and income_group else "NA"

            # Prepare profile image from GridFS
            media = []
            image_ids = user.get("image", [])
            if image_ids:
                file_id = ObjectId(image_ids[0])
                file = db.fs.files.find_one({"_id": file_id})
                chunks_cursor = db.fs.chunks.find({"files_id": file_id}).sort("n", 1)
                base64_chunks = [base64.b64encode(chunk["data"]).decode("utf-8") for chunk in chunks_cursor]
                media.append({
                    "fileId": str(file["_id"]),
                    "filename": file.get("filename", ""),
                    "contentType": file.get("contentType", "image/jpeg"),
                    "length": file.get("length", 0),
                    "chunks": base64_chunks,
                })

            # Construct profile data
            top_data = {
                "Name": f"{user.get('firstName', '')} {user.get('lastName', '')}",
                "Address": f"{user.get('Address', '')} {user.get('CurrentAddress', '')}",
                "Education": f"{user.get('DegDip', '')}, {user.get('Field', '')}",
                "Income": income,
                "Userid": user.get("UserId"),
                "IsVerified": user.get("IsVerified", False),
                "image": media,
                "Birthdate": user.get("birthDate"),
                "Birthtime": user.get("birthTime"),
                "BirthPlace": user.get("BirthPlace"),
                "Bloodgroup": user.get("BloodGrp")
            }
            users.append({"topData": top_data})

        return jsonify({
            "message": "Success",
            "users": users,
            "totalCount": total_count,
            "currentPage": page,
            "rowsPerPage": rows_per_page
        }) 

class DeactivateAccount(Resource):
    @jwt_required()
    def post(self):
        userId = request.json["UserId"]
        deactivationReason = request.json["deactivationReason"]
        try:
            collection = db.get_collection('User')
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            if not currentUser:
                return jsonify({"message": "Failure", "error": "Something Went Wrong"})
            
            currentUser = collection.find_one({"UserId": int(userId)})
            collection.update_one({"UserId": int(userId)},
                                  {"$set":{"IsActive":False,"lastActivity":str(now_local_tz),
                                            "deactivationReason":deactivationReason}})
            return jsonify({"message": "success","redirect":"redirect"})
        except Exception as e:
            print(f"Error fetching users: {e}")
            error_collection = db.get_collection('ErrorLogs')
            error_collection.insert_one({
                "Method": "DeactivateAccount",
                "Exception": str(e),
                "Time": datetime.now()
            })
            return jsonify({"message": "failure"}),200



def profileComplete(user_data):
    number = 0 
    keys_to_check = ["Address","CurrentAddress","birthDate","birthTime","BirthPlace",
                                     "Raas","Height","BloodGrp","Disablity","DegDip","Field","JobBis",
                                     "IncomeGroup","Eating","Gotra","Dosha","Gana","Devak","Nakshatra",
                                     "FamilyType","Siblings","Siblings","EduSiblings","Property",
                                     "EduMother","EduFather","MotherFamily","FatherFamily","degreeName",
                                     "CompanyName","DisabilityYN","Charan","Naadi"
                                     ]
    count = 0
    for key in keys_to_check:
        value = user_data.get(key)  
        if value not in [None, ""]:  
            print(value)
            count += 1
    print(100*count/33)
    print
    if(user_data["UserRole"] =="2"):
        return int(100*count/33)
    else:
        return 100

def ValidateUser(email, password):
    try:
        query = {"UserEmail": email}
        projection = {"_id": 0,"UserPaid":0}
        collection = db.get_collection('User')
        data = collection.find_one(query,projection)
        if data and checkpw(password.encode('utf-8'), data["UserPassword"].encode('utf-8')):
            return data 
        else:
            return None
    except ValueError as e:
        print(f"Error checking password: {e}")
        log = collection.insert_one({"Method":"ValidateUser-UserApi.py","Exception":e,"Time":datetime.datetime.now,"UserEmail":email})
        return None

class GetProfilePicture(Resource):
    def post(self):
        userid = request.json["userid"]
        coll = db.get_collection("User")
        image_doc = coll.find_one({"UserId": int(userid)}, {"image": 1, "_id": 0})
        print("image_docimage_docimage_docimage_docimage_docimage_docimage_doc")
        print(image_doc)
        if len(image_doc["image"]) == 0 :
            return jsonify({"message": "NoDP", "data": []})
        media = []
        
        if(len(image_doc["image"]) > 0):
            print(image_doc["image"][0])
            file_id = ObjectId(image_doc["image"][0])
            print(file_id)
            print(type(file_id))
            file = db.fs.files.find_one({"_id": file_id})
            chunks_cursor = db.fs.chunks.find({"files_id": file_id}).sort("n", 1)
            base64_chunks = [base64.b64encode(chunk["data"]).decode("utf-8") for chunk in chunks_cursor]
            media.append({
            "fileId": str(file["_id"]),
            "filename": file.get("filename", ""),
            "contentType": file.get("contentType", "image/jpeg"),
            "length": file.get("length", 0),
            "chunks": base64_chunks,
            })        
        return jsonify({"message":"success","data":media})

class ChangePassword(Resource):
    @jwt_required()
    def post(self):
        try:
            userId = request.json["userId"]
            NewPassword = request.json["NewPassword"]
            hashed_password = hash_password(NewPassword)
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            collection = db.get_collection("User")
            collection.update_one({"UserId":int(userId)},{"$set":{"lastActivity":str(now_local_tz),"UserPassword":hashed_password.decode('utf-8')}})            

            print(userId)
            print(NewPassword)
            return jsonify({"message":"success","data":"Password Changed Successfully"})
        except Exception as e:
            return jsonify({"message":"failure","data":"Something went wrong"})


class ForgotPassword(Resource):
    def post(self):
        userEmail = request.json["UserEmail"]
        print(userEmail)
        collection = db.get_collection("User")
        data = collection.find_one({"UserEmail":userEmail},{"_id":0})
        if data:
            NewPassWordd = generate_random_string(10)
            hashed_password = hash_password(NewPassWordd)
            collection.update_one({"UserEmail":userEmail},{
                "$set":{
                    "UserPassword":hashed_password.decode('utf-8')
                }
            })
            print(hashed_password)
            return jsonify({"message":"success","data":"Please Check Your Email Address For New Password","NewPaddword":NewPassWordd})
        else:
            return jsonify({"message":"failure","data":"This User is NOT Registered with Vivah Bandhan"})

class GetMyContacts(Resource):
    def get(self):
        print("")
        
class UploadImages(Resource):
    @jwt_required()
    def post(self):
        files = request.files.getlist('file')
        file_ids = []
        try:
            collection = db.get_collection("User")
            data = collection.find_one({"UserEmail":get_jwt_identity()})
            if(len(data["images"]) > 2):
                return jsonify({"message":"failure","data":"Cannot Upload More Than Three Images. Please Delete At Least One Image Before Adding More."})
            for file in files:
                if file:
                    file_id = fs.put(file, filename=file.filename,
                                     metadata={"UserEmail": get_jwt_identity()}
                                     )
                    
                    file_ids.append(str(file_id))
                    print(type(file_id))
                    collection.update_one(
                    {"UserEmail": get_jwt_identity()},
                    {"$addToSet": {"images": str(file_id)}}
                )
            return jsonify({'file_ids': file_ids,"data":"Image uploaded Successfully"})  # Respond with file ids
        except Exception as e:
            print(e)
            return jsonify({'error': str(e),"message":"fail"})

class GetImages(Resource):
    @jwt_required()
    def get(self):
        try:
            user_collection = db.get_collection("User")
            data = user_collection.find_one({"UserEmail":get_jwt_identity()})
            print(get_jwt_identity())
            files = list(db.fs.files.find({ "metadata.UserEmail":get_jwt_identity() }))
            media = []
            for file in files:
                chunks_cursor = db.fs.chunks.find({ "files_id": file["_id"] }).sort("n", 1)
                base64_chunks = [base64.b64encode(chunk["data"]).decode("utf-8") for chunk in chunks_cursor]
                media.append({
                    "fileId": str(file["_id"]),
                    "filename": file.get("filename", ""),
                    "contentType": file.get("contentType", "image/jpeg"),
                    "length": file.get("length", 0),
                    "chunks": base64_chunks,
                })
            return jsonify({ "message": "success", "data": media })
        except Exception as e:
            print(str(e))

class GetImagesById(Resource):
    @jwt_required()
    def get(self):
        media = []
        userId = request.json["userId"]
        try:
            data = user_collection.find_one({"UserId":int(userId)})
            files = list(db.fs.files.find({ "metadata.UserEmail":data["UserEmail"] }))
            for file in files:
                chunks_cursor = db.fs.chunks.find({ "files_id": file["_id"] }).sort("n", 1)
                base64_chunks = [base64.b64encode(chunk["data"]).decode("utf-8") for chunk in chunks_cursor]
                media.append({
                    "fileId": str(file["_id"]),
                    "filename": file.get("filename", ""),
                    "contentType": file.get("contentType", "image/jpeg"),
                    "length": file.get("length", 0),
                    "chunks": base64_chunks,
                })
            return jsonify({"message":"success","data":media})
        except Exception as e:
            print(e)
            return jsonify({"message":"failure","data":media})
            
class DeleteImages(Resource):
    @jwt_required()
    def post(self):
        image_id = request.json["imageId"]
        print(image_id)
        try:
            collection = db.get_collection("User")
            collection.update_one({"UserEmail": get_jwt_identity()},{"$pull": {"images": str(image_id)}})
            db.fs.files.delete_many({ "_id": ObjectId(image_id) })
            db.fs.chunks.delete_many({ "files_id":ObjectId(image_id) })
            return jsonify({"message":"success","data":"Image Deleted Successfully"})
        except Exception as e:
            print(e)
            return jsonify({"message":"failure","data":"Something went wrong. Please try again later"})
            
class SetProfileImage(Resource):
    @jwt_required()
    def post(self):
        image_id = request.json["imageId"]
        print(image_id)
        print(get_jwt_identity())
        collection = db.get_collection("User")
        data = collection.find_one({"UserEmail":get_jwt_identity()})
        
        try:
            print(data["image"])
            if(len(data["image"]) == 0):
                collection.update_one({"UserEmail":get_jwt_identity()},{"$addToSet":{"image":str(image_id)}})
            else:
                collection.update_one({"UserEmail":get_jwt_identity()},{"$set":{"image":[]}})
                collection.update_one({"UserEmail":get_jwt_identity()},{"$addToSet":{"image":str(image_id)}})
            return jsonify({"message":"success","data":"Profile Image Changed Successfully"})
        except Exception as e:
            print(e)
            return jsonify({"message":"failure","data":"Something went wrong. Please try again later"})
        

def generate_random_string(length):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))

def hash_password(password):
    hashed_password = hashpw(password.encode('utf-8'), gensalt())
    return hashed_password

def parse_birth_date(birthDate):
    if not birthDate:
        return None

    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # Standard ISO format
        "%Y-%m-%dT%H:%M:%S.%f",    # ISO without "Z"
        "%Y-%m-%dT%H:%M:%S",       # Without milliseconds
        "%Y-%m-%d",                # Only date
        "%a, %d %b %Y %H:%M:%S %Z" # RFC 1123 format (Thu, 08 Jun 1989 06:06:18 GMT)
    ]

    for fmt in formats:
        try:
            return datetime.strptime(birthDate, fmt)
        except ValueError:
            continue  # Try the next format

    raise ValueError(f"Unsupported date format: {birthDate}")



def checkUserDevice(userEmail,accessToken):
    print("__________________________________________________________________________________")
    print(userEmail)
    token = accessToken.split(" ")[1]
    collection = db.get_collection("User")
    data = collection.find_one({"UserEmail":userEmail})
    if data["access_token"] == token :
        return True
    else:
        return False
    
class VerifyOPT(Resource):
    @jwt_required()
    def post(self):
        otp = request.json["OTP"] 
        PhoneNumber = request.json["PhoneNumber"] 
        try:
            current_user = get_jwt_identity()
            print(current_user)
            print(otp)
            print(PhoneNumber)
            print(datetime.now())
            collectionOTP = db.get_collection("OTPValidations")
            collectionUsers = db.get_collection("User")
            number = "91" + str(PhoneNumber)
            otp_data = collectionOTP.find_one({"UserPhoneNumber":str(number)},sort=[("created_at", -1)])
            print(otp_data)
            if(datetime.now() <= otp_data["ValidTill"]):
                if(otp_data["OTP"] == str(otp)):
                    print("Yes")
                    collectionUsers.update_one({"UserEmail":current_user},{"$set":{"isPhoneVerified":True,"PhoneNumber":PhoneNumber}})
                else:
                    return jsonify({"message":"failure","data":"Invalid OTP"})
            else:
                return jsonify({"message":"failure","data":"This OTP is expired"})
            print("otp_data")
            print(otp_data)
            return jsonify({"message":"success","data":"Your number is verified Successfully!"})
        except Exception as e:
            print(e)
            return jsonify({"message":"failure","data":"Something Went Wrong.Please Try Again Later."})