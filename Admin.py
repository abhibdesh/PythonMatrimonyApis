from flask import Flask, jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource
from firebase_admin import firestore
from bcrypt import gensalt, checkpw, hashpw
from flask_jwt_extended import create_access_token, jwt_required,get_jwt_identity
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

class FetchDashboardData(Resource):
    @jwt_required()
    def post(self):
        try:
            collection = db.get_collection("User")
            allData = []
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
            collection = db.get_collection("User")
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
        

        
        