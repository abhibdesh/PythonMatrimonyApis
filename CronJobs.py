from flask import Flask, jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource
from bcrypt import gensalt, checkpw, hashpw
from flask_jwt_extended import create_access_token, jwt_required,get_jwt_identity
from pymongo import MongoClient
import json
from jwt import DecodeError
from jwt.exceptions import PyJWTError as DecodeError
import datetime
from dateutil.relativedelta import relativedelta
import os
import pytz

mongoURI = os.getenv('MONGO_URL','')
databse = os.getenv('DATABSE',"")
client = MongoClient(mongoURI)
db = client.get_database(databse)

local_timezone = pytz.timezone('Asia/Kolkata')  
now_local_tz = datetime.datetime.now(local_timezone)

TIMESTAMP_NOW = datetime.datetime.fromisoformat(str(now_local_tz))
INACTIVITY_THRESHOLD = TIMESTAMP_NOW - datetime.timedelta(minutes=30)

class CheckActiveUsers(Resource):
    def get(self):
        print("Executing CheckActiveUsers Start")
        collection = db.get_collection('User')
        data = collection.find({"isLoggedIn":1} , {"_id": 0})
        print("INACTIVITY_THRESHOLD")
        print(INACTIVITY_THRESHOLD)
        print("INACTIVITY_THRESHOLD")
        for i in data:
            last_activity = datetime.datetime.fromisoformat(i["lastActivity"])
            if(last_activity < INACTIVITY_THRESHOLD):
                collection.update_one({"UserId":int(i["UserId"])},{
                    "$set":{
                        "lastLogOutTime": str(TIMESTAMP_NOW),
                        "isLoggedIn":0,
                        "access_token":""
                    }
              
            })  
                print(i["lastActivity"] + "   " + str(i["UserId"]))
        print("Executing CheckActiveUsers Done")


class CheckPaymentInfo(Resource):
    def get(self):
        collection = db.get_collection("PaymentInfo")
        data = collection.find({"IsApproved":1,"LimitExhausted":False, "ValidTill": {"$gt":datetime.datetime.now()}})
        for i in data :
            if len(i["savedProfiles"]) < i["ProfileCount"]:
                print("")

        print("Hello")
