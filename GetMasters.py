from flask import make_response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from pymongo import MongoClient
import json
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

class GetNewUserFormMasters(Resource):
    def post(self):
        datalist = []
        listOfData = request.json.get('listOfData')
        try:
            collection = db.get_collection('CategoryMaster')            
            data2 = collection.aggregate([{"$match":{"categoryName":{"$in": listOfData}}},{"$group": { 
                    "_id": "$categoryName", 
                    "values": { "$addToSet": "$categoryValue" } 
                        } 
                    }
                ])

            for d in data2:
                datalist.append(d)
            return jsonify({"data":datalist})
        except ValueError as e:
            collection = db.get_collection('ErrorLogs')
            log = collection.insert_one({"Method":"UserLogin-UserApi.py","Exception":e,"Time":datetime.datetime.now})
            return jsonify({MessageVariable: FailureString, msgVal: "We Apologize For The Inconvenience.Please Try Again Later"})
 

