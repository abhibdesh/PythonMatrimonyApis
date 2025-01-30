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
        collection = db.get_collection("User")
        allData = []
        dataa = {}
        data = collection.find({},{"image":0, "_id":0, "UserPassword":0})
        for i in data:
            allData.append(i)
        print(allData)
        dataa["data"] = allData
        return jsonify({
                "message": "Success",
                "users": allData,
               
            })
        