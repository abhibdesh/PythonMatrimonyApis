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
import calendar

local_timezone = pytz.timezone('Asia/Kolkata')  
now_local_tz = datetime.now(local_timezone)


mongoURI = os.getenv('MONGO_URL','mongodb+srv://abhibdesh:k6fEWav4Dkc1rQzn@mat.podj9wc.mongodb.net/?retryWrites=true&w=majority&appName=Mat')
databse = os.getenv('DATABSE',"Matrimony")
client = MongoClient(mongoURI)
db = client.get_database(databse)

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

class FetchAdminDashboard(Resource):
    @jwt_required()
    def post(self):
        try:
            print("FetchAdminDashboard")
            cu = get_jwt_identity()
            referals = []
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            UserCollection = db.get_collection("User")
            UserCollection.update_one({"UserEmail":get_jwt_identity()},{"$set":{"lastActivity":str(now_local_tz)}})
            admin = db.get_collection("AdminMapping")
            adminCode = admin.find_one({"AdminEmail":cu})
            col = db.get_collection("User")
            print(adminCode['ReferenceCode'] )
            data = col.find({"ReferenceCode":adminCode['ReferenceCode'],},{"_id":0})
            for i in data:
                print(i)
                referals.append(i)
                return jsonify({"message":"success", "data":referals})
        except:
            return jsonify({"message":"failure","data":[]})
        

class FetchDashboardData(Resource):
    @jwt_required()
    def post(self):
        try:
            currentUser = get_jwt_identity()
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            else:
                collection = db.get_collection("User")
                curUser = collection.find_one({"UserEmail":currentUser})
                collection.update_one({"UserEmail":get_jwt_identity()},{"$set":{"lastActivity":str(now_local_tz)}})
                allData = []
                if curUser["UserRole"] == "3":
                    adminMapp = db.get_collection("AdminMapping")
                    d = adminMapp.find_one({"AdminEmail":currentUser})
                    data = collection.find({"ReferenceCode":d["ReferenceCode"],"UserRole":"2"},{"image":0, "_id":0, "UserPassword":0,"access_token":0})
                    print("asd")
                    for i in data:
                        allData.append(i)
                else:
                    data = collection.find({},{"image":0, "_id":0, "UserPassword":0})
                    for i in data:
                        allData.append(i)
                return jsonify({
                        "message": "Success",
                        "users": allData, 
                    })
        except Exception as e:
            print(f"Error checking password: {e}")
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"FetchDashboardData-Admin.py","Exception":e,
                                         "Time":datetime.now})
            return jsonify({"msg":"failure","data":"Something Went Wrong. Please Try Again Later"})

    
class VerifyAccount(Resource):
    @jwt_required()
    def post(self):
        userId = request.json["userId"]
        print("userId")
        print(userId)
        try:
            if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
                return jsonify({"message": "Failure","data":"Session Timed Out"})
            collection = db.get_collection("User")
            collection.update_one({"UserEmail":get_jwt_identity()},{"$set":{"lastActivity":str(now_local_tz)}})
            data = collection.update_one({"UserId":int(userId)},{"$set":{ "IsVerified":"1"}})
            return jsonify({"msg":"success","data":"This Profile is verified"})
        except Exception as e:
            print(f"Error checking password: {e}")
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"VerifyAccount-Admin.py","Exception":e,
                                         "Time":datetime.now})
            return jsonify({"msg":"failure","data":"Something Went Wrong. Please Try Again Later"})


class FetchAllUsersAdmin(Resource):
    @jwt_required()
    def post(self):
        print("ADMIN DASHBOARD")
        current_user = get_jwt_identity()
        # current_user = "abhibdesh@gmail.com"
        print("Authenticated User:", current_user)
        filters = request.json['filters']
        isPaidUser = request.json["isPaid"]
        page = int(request.json['pageNumber'])
        rowsPerPage = int(request.json['rowsPerPage'])
        Userid = request.json["Userid"]
        if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
            return jsonify({"message": "Failure","data":"Session Timed Out"})
        userCollection = db.get_collection("User")
        userCollection.update_one({"UserEmail":get_jwt_identity()},{"$set":{"lastActivity":str(now_local_tz)}})

        finaldataList = []
        cu = userCollection.find_one({"UserId": int(Userid)})
        projection = {"_id":0}
        try:
            if cu["UserRole"] == "3":
                adminMapp = db.get_collection("AdminMapping")
                d = adminMapp.find_one({"AdminEmail":cu["UserEmail"]})
                data = userCollection.find({"ReferenceCode":d["ReferenceCode"],"UserRole":"2"},{"image":0, "_id":0, "UserPassword":0,"access_token":0})
                print("asd")
                total_count = userCollection.count_documents({"ReferenceCode":d["ReferenceCode"],"UserRole":"2"}) 
                data = (
                    userCollection.find({"ReferenceCode":d["ReferenceCode"],"UserRole":"2"},{ "_id":0, "UserPassword":0,"access_token":0})
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
                        "Address": str(u['Address']) + ' ' + str(u["CurrentAddress"]),
                        "Education": str(u["DegDip"]) + ', ' + str(u['Field']),
                        "Income": income,
                        "Userid": u['UserId'],
                        "IsVerified":u["IsVerified"],
                        "image": "" if (u['image'] == None)  else u['image'] ,
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
            else:
                print("asdasd")

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

            
                filters["IsDeleted"] = False
                collection = db.get_collection('User')
                curUser = collection.find_one({"UserEmail":current_user})
                if(curUser["isLoggedIn"] == 0):
                    return jsonify({"message": "Failure", "error": "Something Went Wrong"})
                currentUser = collection.find_one({"UserId": Userid}, projection)
                if not currentUser:
                    return jsonify({"message": "User not found", "users": []})

                newFilter = {"UserId": {"$ne": Userid}, "IsDeleted": False, "IsActive":True }
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
                        "Address": str(u['Address']) + ' ' + str(u["CurrentAddress"]),
                        "Education": str(u["DegDip"]) + ', ' + str(u['Field']),
                        "Income": income,
                        "Userid": u['UserId'],
                        "IsVerified":u["IsVerified"],
                        "image": "" if (u['image'] == None)  else u['image'] ,
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
        

        
class PromoteToAdmin(Resource):
    @jwt_required()
    def post(self):
        userId = request.json["UserId"]
        userCollection = db.get_collection("User")
        adminCollection = db.get_collection("AdminMapping")
        if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
            return jsonify({"message": "Failure","data":"Session Timed Out"})
        data = userCollection.find_one({ "UserId": int(userId)})
        userCollection.update_one({"UserEmail":get_jwt_identity()},{"$set":{"lastActivity":str(now_local_tz)}})
        name = data["firstName"] + data["lastName"]
        refCode = (name[0:3]).upper()+str(random.randint(1000, 9999))
        admin = adminCollection.find_one({"AdminEmail":data["UserEmail"]})
        if(admin):
            print(admin)
            adminCollection.update_one({"AdminEmail":admin["AdminEmail"]},{"$set":{"ReferenceCode" : refCode}})
            userCollection.update_one({
            "UserId": int(userId)
        },
        {"$set":{
            "UserRole":"3",
            "ReferenceCode":refCode
        }}
        )
        else:
            adminCollection.insert_one({
            "AdminEmail":data["UserEmail"],
            "ReferenceCode":refCode,
            "CreatedDateTime": datetime.now()
            })
            userCollection.update_one({
            "UserId": int(userId)
        },
        {"$set":{
            "UserRole":"3",
            "ReferenceCode":refCode
        }}
        )
       
      


class GetAllReferenceCodes(Resource):
    def get(self):
        # This will be used to validate id the user is putting right reference code
        adminCodes = []
        col = db.get_collection("AdminMapping")
        data = col.find({},{"_id":0})
        for d in data:
            adminCodes.append(d["ReferenceCode"])
        print(adminCodes)
        return jsonify({"message":"success","data":adminCodes})

class GetMyReferences(Resource):
    @jwt_required()
    def post(self):
        # This will be used for ADMINS to see how much business they got.
        cu = get_jwt_identity()
        pagenumber = int(request.json["pageNumber"])
        rowsPerPage = int(request.json["rowsPerPage"])
        referals = []
        if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
            return jsonify({"message": "Failure","data":"Session Timed Out"})
        userCollection = db.get_collection("User")
        userCollection.update_one({"UserEmail":get_jwt_identity()},{"$set":{"lastActivity":str(now_local_tz)}})
        admin = db.get_collection("AdminMapping")
        adminCode = admin.find_one({"AdminEmail":cu})
        col = db.get_collection("PaymentInfo")
        total_Count = col.count_documents({
            "ReferenceCode":adminCode['ReferenceCode'],
            "IsApproved":1,
        })
        data = col.find({
            "ReferenceCode":adminCode['ReferenceCode'],
            "IsApproved":1
        },{"_id":0}).skip((pagenumber-1)*rowsPerPage).limit(rowsPerPage)
        for i in data:
            referals.append(i)
        return jsonify({"message":"success","data":referals,"totalCount":total_Count})
    
class DownloadMyPaymentSettlement(Resource):
    @jwt_required()
    def get(self):
        cu = get_jwt_identity()
        referals = []
        if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
            return jsonify({"message": "Failure","data":"Session Timed Out"})
        userCollection = db.get_collection("User")
        userCollection.update_one({"UserEmail":cu},{"$set":{"lastActivity":str(now_local_tz)}})
        admin = db.get_collection("AdminMapping")
        adminCode = admin.find_one({"AdminEmail":cu})
        col = db.get_collection("PaymentInfo")
        data = col.find({
            "ReferenceCode":adminCode['ReferenceCode'],
            "IsApproved":1
        },{"_id":0})
        for i in data:
            referals.append(i)
        return jsonify({"message":"success","data":referals})

class GetAggregateAmount(Resource):
    @jwt_required()
    def get(self):
        referalsdic = {}
        cu = get_jwt_identity()
        if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
            return jsonify({"message": "Failure","data":"Session Timed Out"})
        admin = db.get_collection("AdminMapping")
        adminCode = admin.find_one({"AdminEmail":cu})
        col = db.get_collection("PaymentInfo")
        pipeline = [
            {
                "$match": {  # Filter documents based on ReferenceCode and IsApproved
                    "ReferenceCode": adminCode['ReferenceCode'],
                    "IsApproved": 1,
                    "IsPaymentSettled":False
                }
            },
            {
                "$group": {
                    "_id": {
                        "ReferenceCode": "$ReferenceCode",
                        "month": {"$month": "$CreatedDate"},  
                        "year": {"$year": "$CreatedDate"}    
                    },
                    "totalAmount": {"$sum": {"$toDouble": "$amount"}} 
                }
            },
            {
                "$sort": {"_id.year": 1, "_id.month": 1}
            }
        ]
        result = list(col.aggregate(pipeline))
        for entry in result:
            referalsdic["Month"] = getMonthName(entry['_id']['month'])
            referalsdic["Year"] = entry['_id']['year']
            referalsdic["Amount"] = entry['totalAmount']
        return jsonify({"message":"success","data":referalsdic})
        
        
class GetPaymentSettlement(Resource):
    @jwt_required()
    def post(self):
        cu = get_jwt_identity()
        pagenumber = int(request.json["pageNumber"])
        rowsPerPage = int(request.json["rowsPerPage"])
        if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
            return jsonify({"message": "Failure","data":"Session Timed Out"})
        col = db.get_collection("PaymentInfo")
        pipeline = [
            {
                "$match": {  # Filter documents based on ReferenceCode and IsApproved
                    "IsApproved": 1,
                    "IsPaymentSettled":False
                }
            },
            {
                "$group": {
                    "_id": {
                        "ReferenceCode": "$ReferenceCode",
                        "month": {"$month": "$CreatedDate"},  
                        "year": {"$year": "$CreatedDate"}    
                    },
                    "totalAmount": {"$sum": {"$toDouble": "$amount"}} ,
                    
                }
            },
            {
                "$sort": {"_id.year": 1, "_id.month": 1}
            }
        ]
        result = list(col.aggregate(pipeline))
        referals = []
        for entry in result:
            referalsdic = {}
            referalsdic["Month"] = getMonthName(entry['_id']['month'])
            referalsdic["Year"] = entry['_id']['year']
            referalsdic["Amount"] = entry['totalAmount']
            referalsdic["ReferenceCode"] = entry['_id']['ReferenceCode']
            referals.append(referalsdic)
        totalCount = len(referals)
        return jsonify({"message":"success","data":referals,"totalCount":totalCount})
    
class SettlePaymentOwner(Resource):
    @jwt_required()
    def post(self):
        ReferenceCode = request.json['ReferenceCode']
        print(ReferenceCode)
        print("Settled")
        if(checkUserDevice(get_jwt_identity(),request.headers.get("Authorization")) == False):
            return jsonify({"message": "Failure","data":"Session Timed Out"})
        paymentCollection = db.get_collection("PaymentInfo")
        paymentCollection.update_many({"ReferenceCode":ReferenceCode},{"$set":{"IsPaymentSettled":True}})
        return jsonify({"message": "success","data":"Payment Settled Successfully"})
        
def getMonthName(number):
    return calendar.month_name[number]
    



