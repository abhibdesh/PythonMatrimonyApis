from flask import request, jsonify
from flask_restful import Resource
from firebase_admin import firestore
from bcrypt import gensalt, checkpw, hashpw
from flask_jwt_extended import create_access_token
from pymongo import MongoClient
import json


with open('./Config/Creds.json') as f:
    config = json.load(f)
    mongoURI = config['uri']
    databse = config['database']
client = MongoClient(mongoURI)
db = client.get_database(databse)



class UserLogin(Resource):
    def post(self):
        email = request.json.get('email')
        password = request.json.get('password')
        user_data = ValidateUser(email, password)  
        access_token = create_access_token(identity=email)
        
        if user_data:
            return jsonify({"message": "Success", "user_data": user_data, 'accessToken': access_token})
        else:
            return jsonify({"message": "Failure", "user_data": "Invalid Credentials"})


class AddNewUser(Resource):
    def post(self):
        email = request.json['email']
        password = request.json['password']
        phoneNumber = request.json['phoneNumber']
        

       
        

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
        return None


def AddUser():
    return False

def hash_password(password):
    hashed_password = hashpw(password.encode('utf-8'), gensalt())
    return hashed_password
