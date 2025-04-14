from flask import Flask, jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_header,get_jwt_identity
from pymongo import MongoClient
import json
from jwt import DecodeError
from jwt.exceptions import PyJWTError as DecodeError
import os
import pytz
import datetime

mongoURI = os.getenv('MONGO_URL','mongodb+srv://abhibdesh:k6fEWav4Dkc1rQzn@mat.podj9wc.mongodb.net/?retryWrites=true&w=majority&appName=Mat')
databse = os.getenv('DATABSE',"Matrimony")
client = MongoClient(mongoURI)
db = client.get_database(databse)

local_timezone = pytz.timezone('Asia/Kolkata')  
now_local_tz = datetime.datetime.now(local_timezone)

class UpdateUserCollection(Resource):
    def post(self):
        print("start")
        print(now_local_tz)
        collection = db.get_collection('AdminMapping')
        collection.update_many({"AdminEmail": {"$in":["coadmin2@vb.com"]}}, [{ "$set": { "communitiesList": ["96 Kuli Maratha"]} }])

        # collection.update_many({
        #     "UserEmail": {"$in":["fyjixtech@gmail.com","coadmin1@vb.com","coadmin2@vb.com"]} 
        #     },{
        #     "$set":{
        #         "isPhoneVerified":True,
        #     }
        # })
       
        # collection.update_one({"UserId":1},
        #                        {"$set":
        #                         {
        #                             "lastActivity":str(now_local_tz)
                                    # ,
                                    # "ProfileCount":True,
                                    # "isEmailVerified":True,
                                    # "ProfilesViewd":0,
                                    # "ProfilesList":[]
                                    # "birthDate" : None,
                                    # "birthTime" : None,
                                    # "age" : None
                                #     "expectedAgeGapMin":0,
                                #  "expectedAgeGapMax":0,
                                #  "selectedBloodGroups" : [],
                                #  "selectedNaadi" : [],
                                #  "selectedRaas":[],
                                #  "selectedHeight":0,
                                #  "selectedFamilyType" :[],
                                #  "selectedSiblingsCousinsUpto":[],
                                #  "strictMatch": True,
                                #  "profileWithImages" : True
                                 
                                #  }
                                # })
        # collection.update_many(

        #     { "readTCP": { "$exists": False } }, 
        #     { "$set": { "readTCP": True } }
        # );         
        print("End")
        return jsonify({"MessageVariable":"DONE"})


class TruncateAllCollections(Resource):
    def post(self):
        userCollection = db.get_collection('User')
        adminCollection = db.get_collection('AdminMapping')
        paymentCollection = db.get_collection('PaymentInfo')

        userCollection.delete_many({})
        adminCollection.delete_many({})
        paymentCollection.delete_many({})


