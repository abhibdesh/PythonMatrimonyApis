from flask import make_response, request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required
from pymongo import MongoClient
import json
from datetime import datetime
import os
import pytz


mongoURI = os.getenv('MONGO_URL','mongodb+srv://abhibdesh:k6fEWav4Dkc1rQzn@mat.podj9wc.mongodb.net/?retryWrites=true&w=majority&appName=Mat')
databse = os.getenv('DATABSE',"Matrimony")
client = MongoClient(mongoURI)
db = client.get_database(databse)


local_timezone = pytz.timezone('Asia/Kolkata')  
now_local_tz = datetime.now(local_timezone)

with open('./Config/Strings.json') as g:
    Strings = json.load(g)
    MethodName = Strings['METHOD_NAME']
    ApiName = Strings['API_NAME']
    SuccessString = Strings['SUCCESS_STRING']
    FailureString = Strings['FAILURE_STRING']
    MessageVariable = Strings['MESSAGE_VARIABLE']
    msgVal=Strings['MESSAGE_VALUE']

class GetNewUserFormMasters(Resource):
    @jwt_required()
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
 

