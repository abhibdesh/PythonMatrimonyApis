from flask import Flask, jsonify, request
from flask_cors import cross_origin
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_header,get_jwt_identity
from pymongo import MongoClient
import json
from jwt import DecodeError
from jwt.exceptions import PyJWTError as DecodeError

with open('./Config/Creds.json') as f:
    config = json.load(f)
    mongoURI = config['uri']
    databse = config['database']
client = MongoClient(mongoURI)
db = client.get_database(databse)


class UpdateUserCollection(Resource):
    def post(self):
        print("start")
        collection = db.get_collection('User')
        collection.update_many({},
                               {"$set":
                                {
                                    "PlanTimeSelected":True,
                                    "ProfileCount":True,
                                    "isEmailVerified":True,
                                    "ProfilesViewd":0,
                                    "ProfilesList":[]
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
                                 
                                 }
                                })
        # collection.update_many(

        #     { "readTCP": { "$exists": False } }, 
        #     { "$set": { "readTCP": True } }
        # );         
        print("End")
        return jsonify({"MessageVariable":"DONE"})
