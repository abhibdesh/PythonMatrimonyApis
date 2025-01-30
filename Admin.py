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
        
        