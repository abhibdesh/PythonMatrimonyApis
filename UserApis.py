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
from dateutil.relativedelta import relativedelta
from pymongo import DESCENDING



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
            collection = db.get_collection('User')
            # collection.update_one()yyy
            if user_data:
                if(user_data["IsActive"] == True):
                    collection.update_one({"UserEmail":email},{"$set":
                                                               {
                                                                   "LastLogin":datetime.now(),
                                                                   "lastActivity" : datetime.now()
                                                                   }
                                                                })
                    return jsonify({MessageVariable: SuccessString, msgVal: user_data, 'accessToken': access_token})
                else:
                    return jsonify({MessageVariable: FailureString, msgVal: "This Account is Deactivated. Please Contact Support For Reactivation.", 'accessToken': access_token})

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
                                                "CreatedDatetime": current_time,
                                                "lastActivity": current_time,
                                                "selectedLocatities":selectedLocatities,
                                                "LastLogin":current_time,
                                                "lastLogOutTime": None,
                                                "expectedNakshatra":expectedNakshatra,
                                                "strictMatch":strictMatch,
                                                "CreatedBy":"User",
                                                "IsActive":True,
                                                "IsDeleted":False,
                                                "UserRole":"2",
                                                "UserPaid":False,
                                                "IsVerified":"0",
                                                 "UserId": 
                                                 userIdNew,
                                                 "image":None,
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
                                                 "profileWithImages": False
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
        #Step 4
        selectedIncome = request.json['selectedIncome']
        eatingHabits = request.json['eatingHabits']
        expectedGana = request.json['expectedGana']     
        selectedEducations = request.json['selectedEducations']
        expectedNakshatra = request.json['expectedNakshatra']
        expectedAgeGapMin = request.json['expectedAgeGap']
        expectedAgeGapMin = request.json['expectedAgeGap']
        selectedLocatities = request.json['selectedLocatities']
        # New Fields
        strictMatch = request.json['strictMatch']
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
                date_obj = datetime.strptime(birthDate, '%Y-%m-%dT%H:%M:%S.%fZ')
                # date_obj = datetime.strptime(birthDate, '%a, %d %b %Y %H:%M:%S %Z')
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
                        "lastActivity":datetime.now(),
                        "CurrentAddress":CurrentAddress,
                        "birthDate":date_obj,
                        "birthTime":time.strftime("%H:%M:%S"),
                        "age":age,
                        "BirthPlace":BirthPlace,"Raas":Raas,
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
                        "degreeName":degreeName,
                        "CompanyName":CompanyName,
                        "DisabilityYN":DisabilityYN,
                        "Charan":Charan, 
                        "Naadi":Naadi,
                        "CreatedBy":"User",
                        "IsActive":True,
                        "IsDeleted":False,
                        "UserRole":"2",
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
                        "lastActivity":datetime.now(),
                        "birthTime":time.strftime("%H:%M:%S"),
                        "Address":Address,
                        "CurrentAddress":CurrentAddress,
                        "BirthPlace":BirthPlace,"Raas":Raas,
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
                        "degreeName":degreeName,
                        "CompanyName":CompanyName,
                        "DisabilityYN":DisabilityYN,
                        "Charan":Charan, "Naadi":Naadi,
                        "CreatedBy":"User",
                        "IsActive":True,
                        "IsDeleted":False,
                        "UserRole":"2",
                        "image":image
                        }

            if(birthDate != None and birthTime == None):
                # BIRTH DATE SECTION
                print("ONLY BITHDATE")

                date_obj = datetime.strptime(birthDate, '%a, %d %b %Y %H:%M:%S %Z')
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
                    "lastActivity":datetime.now(),
                    "CurrentAddress":CurrentAddress,
                    "birthDate":date_obj,
                    "age":age,
                    "BirthPlace":BirthPlace,"Raas":Raas,
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
                    "degreeName":degreeName,
                    "CompanyName":CompanyName,
                    "DisabilityYN":DisabilityYN,
                    "Charan":Charan, "Naadi":Naadi,
                    "CreatedBy":"User",
                    "IsActive":True,
                    "IsDeleted":False,
                    "UserRole":"2",
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
                        "Height": Height,
                        "BloodGrp":BloodGrp,
                        "lastActivity":datetime.now(),
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
                        "UserRole":"2",
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
           
            # date_obj = datetime.strptime(, '%a, %d %b %Y %H:%M:%S %Z')
            collection = db.get_collection('User')
            collection.update_one({"UserId":int(UserId)},{"$set":newData})
        except Exception as e:
            print("Error:", e)
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"UpdateProfile-UserApi.py","Exception":e,"Time":datetime.now})
            return jsonify({"message": "An error occurred during logout", "error": str(e)}), 500

        
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
            print("k")
            collection = db.get_collection('User')
            newdata = {
                "lastActivity":datetime.now(),
                "selectedIncome":selectedIncome,
                "eatingHabits":eatingHabits,
                "expectedGana":expectedGana,
                "selectedEducations":selectedEducations,
                "expectedNakshatra":expectedNakshatra,
                "strictMatch":strictMatch,
                "selectedLocatities":selectedLocatities,
                "expectedAgeGapMin":float(expectedAgeGapMin),
                "expectedAgeGapMax":float(expectedAgeGapMax),
                "selectedBloodGroups":selectedBloodGroups,
                "selectedNaadi":selectedNaadi,
                "selectedRaas":selectedRaas,
                "selectedHeight":selectedHeight,
                "selectedFamilyType":selectedFamilyType,
                "selectedSiblingsCousinsUpto":selectedSiblingsCousinsUpto,
                "profileWithImages":profileWithImages,
            }
            print(newdata)
            collection.update_one({"UserId":int(UserId)},{"$set":newdata})
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
        print(userId)
        try:
            print(current_user)
           
            newFilter = {"UserId" : int(userId)}
            print(newFilter)
            collection = db.get_collection('User')
            collection.update_one({"UserEmail":current_user},{
                "$set":{"lastActivity":datetime.now()}
            })
            curr_user =  collection.find_one({"UserEmail":current_user})
            print(curr_user["isPhoneVerified"])
            print(curr_user["isEmailVerified"])
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
            if curr_user["UserPaid"] == True:
                if curr_user["isEmailVerified"] == True:
                    final_data["UserEmail"] = data["UserEmail"]
                else:
                    final_data["UserEmail"]  = "Verify Your Email"      
            else:
              final_data["UserEmail"] = "Buy Our Services For Contact Information"
            
            if curr_user["UserPaid"] == True:
                if curr_user["isPhoneVerified"] == True:
                    final_data["PhoneNumber"] = data["PhoneNumber"]
                else:
                    final_data["PhoneNumber"]  = "Verify Your Mobile Number"      
            else:
              final_data["PhoneNumber"] = "Buy Our Services For Contact Information"

            final_data["JobBis"]= data["JobBis"] if  data["JobBis"] != "" else "Not Provided"
            final_data["DegDip"]= data["DegDip"] if data["DegDip"] !="" else "Not Provided"
            final_data["FieldOrPost"]= data["Field"] if data["Field"] !="" else "Not Provided"
            final_data["DegreeName"]= data["degreeName"] if data["degreeName"] !="" else "Not Provided"
            final_data["CompanyName"]= data["CompanyName"] if data["CompanyName"] !="" else "Not Provided"
            final_data["IncomeGroup"]= data["IncomeGroup"] if data["IncomeGroup"] !="" else "Not Provided"
            final_data["CurrentAddress"]= str(data["Address"])+", " + str(data["CurrentAddress"]) if str(data["Address"])+", " + str(data["CurrentAddress"]) != "" else "Not Provided"
            # Mandatory to know for patrika match section
            if data["birthDate"] == None:
                final_data["BirthDate"]  = "Not Provided"
            else:
                final_data["BirthDate"] = str(data["birthDate"].date())+", "+day_name + " (YYYY-MM-DD)" 
            final_data["BirthTime"]= data["birthTime"] + " (24 Hour Clock Format)" if data["birthTime"] is not None else "Not Provided"
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
            final_data["expectedAgeGap"]= str(data["expectedAgeGapMin"]) + "-"  + str(data["expectedAgeGapMax"]) if str(data["expectedAgeGapMin"])  != "0" and str(data["expectedAgeGapMax"]) != "0" else "No bar"
            final_data["strictMatch"]= "Yes" if data["strictMatch"] == True else "No" 
            final_data["IsVerified"] = "1" if data["IsVerified"] == "1" else "0" 
            print( final_data["IsVerified"])
            print( "final_data[""]")
            return jsonify({MessageVariable:SuccessString,"data":final_data})
        except Exception as e:
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"GetSingleProfileData-UserApi.py","Exception":e,"Time":datetime.now})
            return jsonify({MessageVariable: FailureString, msgVal: "Something Went Wrong"})



class LogoutUser(Resource):
    @jwt_required()
    def post(self):
        try:
            current_user = get_jwt_identity()
            print("Authenticated User:", current_user)
            collection = db.get_collection("User")
            collection.update_one({"UserEmail":current_user},{
                "$set":{
                    "lastActivity":datetime.now(),
                    "lastLogOutTime":datetime.now()
                    }
            })
            return jsonify({MessageVariable: "Done"})
        except Exception as e:
            print("Error:", e)
            return jsonify({"message": "An error occurred during logout", "error": str(e)}), 500


class FetchMyProfile(Resource):
    def post(self):
        userid = request.json["UserId"]
        # current_user = get_jwt_identity()
        # print("Authenticated User:", current_user)
        try:
            projection = {"_id": 0,"UserPassword":0}
            newFilter = {"UserId" : int(userid)}
            print(newFilter)
            collection = db.get_collection('User')
            collection.update_one(newFilter,{
                "$set":{
                    "lastActivity":datetime.now(),
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
        # current_user = get_jwt_identity()
        # print("Authenticated User:", current_user)
        filters = request.json['filters']
        isPaidUser = request.json["isPaid"]
        page = int(request.json['pageNumber'])
        rowsPerPage = int(request.json['rowsPerPage'])
        Userid = request.json["Userid"]

        projection = {"_id": 0, "UserPassword": 0}
        if not isPaidUser:
            projection.update({"UserEmail": 0, "PhoneNumber": 0})
        print("asdasd")
        print(filters)
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

        try:
            filters["IsDeleted"] = False
            collection = db.get_collection('User')
            currentUser = collection.find_one({"UserId": int(Userid)}, projection)
            if not currentUser:
                return jsonify({"message": "User not found", "users": []})
            
            collection.update_one({"UserId": int(Userid)},{
                "$set":{
                    "lastActivity":datetime.now()
                }
            })

            newFilter = {"UserId": {"$ne":int(Userid)}, "IsDeleted": False, "IsActive":True, "LookingFor": {"$ne": currentUser.get("LookingFor")} }
            if int(filters["selectedFromHeight"]) > 0 :
                newFilter["Height"] = {"$gte": int(filters["selectedFromHeight"])}
            if int(filters["selectedToHeight"]) > 0 :
                newFilter["Height"] = {"$lte": int(filters["selectedToHeight"])}
            if int(filters["expectedAgeGapMin"]) > 0 and currentUser["expectedAgeGapMin"] > 0:
                currentUserAge = float(currentUser["age"])
                lessThanAge = currentUserAge - int(currentUser["expectedAgeGapMin"])
                newFilter["age"] = {"$gte": lessThanAge}
            if int(filters["expectedAgeGapMax"]) > 0 and currentUser["expectedAgeGapMin"] > 0:
                currentUserAge = float(currentUser["expectedAgeGapMax"])
                greterThanAge = currentUserAge + int(currentUser["expectedAgeGapMax"]) 
                newFilter["age"] = {"$lte": greterThanAge}
            # newFilter["age"] = {"$gte": lessThanAge, "$lte":greterThanAge}


             
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
            
            print(newFilter)

            total_count = collection.count_documents(newFilter) 
          
            data = (
                collection.find(newFilter, projection)
                .skip((page - 1) * rowsPerPage) 
                .limit(rowsPerPage)  
            )

            for u in data:
                income = "Income Details Not Provided"
                print(u["birthDate"])
                if u["JobBis"] and u['IncomeGroup']:
                    income = u["JobBis"] + ", earns " + u['IncomeGroup']

                top_data = {
                    "Name": u['firstName'] + ' ' + u["lastName"],
                    "Address": str(u['Address']) + ', ' + str(u["CurrentAddress"]),
                    "Education": str(u["DegDip"]) + ', ' + str(u['Field']),
                    "Income": income,
                    "Userid": u['UserId'],
                    "IsVerified":u["IsVerified"]

                   
                }

                next_Data = {
                    "Birthdate": u['birthDate'],
                    "Birthtime": u['birthTime'],
                    "BirthPlace": u['BirthPlace'],
                    "Bloodgroup": u["BloodGrp"]
                     ,"image": u['image']
                      ,"Userid": u['UserId']
                }

                finaldataList.append({"topData": top_data, "next_data": [next_Data]})

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
        

class DeactivateAccount(Resource):
    @jwt_required()
    def post(self):
        userId = request.json["UserId"]
        deactivationReason = request.json["deactivationReason"]
        try:
            print(deactivationReason)
            print(userId)
            collection = db.get_collection('User')
            currentUser = collection.find_one({"UserId": int(userId)})
            if not currentUser:
                return jsonify({"message": "Failure", "error": "Something Went Wrong"})
            
            collection.update_one({"UserId": int(userId)},
                                  {"$set":{"IsActive":False,"lastActivity":datetime.now(),
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

        
class GetMyPayments(Resource):
    def post(self):
        userId = request.json["userId"]
        today_date = datetime.now() 
        print("userIduserIduserIduserIduserIduserIduserIduserIduserIduserId")
        print(userId)
        print("userIduserIduserIduserIduserIduserIduserIduserIduserIduserId")
        collection = db.get_collection("User")
        collection.update_one({ "UserId": int(userId)},{
            "lastActivity": datetime.now()
        })
        result = db.User.aggregate([
            {
                "$match": {  
                    "UserId": int(userId)
                }
            },
            {
                "$lookup": { 
                    "from": "PaymentInfo",
                    "localField": "UserId",
                    "foreignField": "UserId",
                    "as": "payments",
                    "pipeline": [
                        {
                            "$addFields": {
                                "isActive": { "$gt": ["$ValidTill", today_date] }  
                            }
                        },
                        { "$sort": { "CreatedDate": DESCENDING } },  
                        { "$project": { "_id": 0 }}  
                    ]
                }
            },
            {
                "$project": {
                    "_id": 0,  
                    "payments": 1  
                }
            }
        ])            

        paymentData = []
        hasActivePlan = False 

        for doc in result:
            for payment in doc.get("payments", []):
                if payment.get("isActive"): 
                    hasActivePlan = True
            paymentData.append(doc)

        return jsonify({
            "message": "success",
            "data": paymentData,
            "hasActivePlan": hasActivePlan  
        })

class AddMyPaymentInfo(Resource):
    def post(self):
        userId = request.json["userId"]
        transactionId = request.json["transactionId"]
        plan = request.json["plan"]

        collection = db.get_collection("User")
        collection.update_one({
            "UserId":int(userId)
        },{
            "$set":{
                "lastActivity": datetime.now()
            }
        })
        if plan == "Yearly":
            ValidTill =  datetime.now() + relativedelta(months=12)
            amount = 10000
        if plan == "Monthly":
            ValidTill =  datetime.now() + relativedelta(months=1)
            amount = 6000
        if plan == "Quarterly":
            ValidTill =  datetime.now() + relativedelta(months=3)
            amount = 4000
        if plan == "Half-Yearly":
            ValidTill =  datetime.now() + relativedelta(months=6)
            amount = 7000
        if plan == "Minutes":
            ValidTill =  datetime.now() + relativedelta(minutes=1)
            amount = 20000

        try:
            newData = {
                "UserId" : int(userId),
                "TransactionId": transactionId,
                "CreatedDate" : datetime.now(),
                "ValidTill": ValidTill,
                "Plan": plan,
                "Amount": amount
            }
            collection = db.get_collection("PaymentInfo")
            id = collection.insert_one(newData)
            print(id)
            return jsonify({"Message":"Success","data":str(id)})
        except Exception as e:
            return jsonify({"Message":"Failure","data":str(e)})



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
