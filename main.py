from flask import Flask, redirect, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from itsdangerous import URLSafeTimedSerializer
from pymongo import MongoClient
from UserApis import UserLogin,UpdatePreferences, AddNewUser,DeactivateAccount, FetchAllUsers, FetchMyProfile, LogoutUser, UpdateProfile, GetSingleProfileData
from UpdateExistingRecords import UpdateUserCollection
from GetMasters import GetNewUserFormMasters
from datetime import timedelta
import json
import os

app = Flask(__name__)
api = Api(app)
CORS(app
    #  , resources={r"/*": {
    #     "origins": "http://localhost:5173"
    #                      , "allow_headers": "Authorization"
    #                       }
    #               }
     )
service_account_key = './Config/FirebaseCreds.json'
with open('./Config/Creds.json') as f:
    config = json.load(f)
    mongoURI = config['uri']
    databse = config['database']
client = MongoClient(mongoURI)
db = client.get_database(databse)
app.config['JWT_SECRET_KEY'] = os.getenv('SECERT_KEY')
# serializer = URLSafeTimedSerializer(os.getenv('SECERT_KEY'))
serializer = URLSafeTimedSerializer("asdfghjklpoiuytrewfgvoobndcksdhfjgjhejbdsjbcsbh")
# app.config['JWT_SECRET_KEY'] = "asdfghjklpoiuytrewfgvbndcksdhfjgjhejbdsjbcsbh" # Dummy Key 
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

class HelloWorld(Resource):
    def get(self):
        try:
            return {"hello":"wrold"}
        except Exception as e:
            print(e)
            return {"data": "HelloWorld!!!"}


def send_verification_email(user_email):
    token = serializer.dumps(user_email, salt='email-verify')
    verification_link = f"https://pythonmatrimonyapis.onrender.com/verify-email?token={token}"    
    # verification_link = f"http://127.0.0.1:5000/verify-email?token={token}"    
    print(token)
    return verification_link
   
@app.route('/verify-email', methods=['GET'])
def verify_email():
    token = request.args.get('token')
    print(token)
    if not token:
        return jsonify({"error": "Token is required"}), 400
    try:
        email = serializer.loads(token, salt='email-verify', max_age=3600)
        print("999999999999999999999")
        print(email)
        collection = db.get_collection("User")
        collection.update_one({"UserEmail":email},{"$set":{"isEmailVerified":True}})
        # return redirect(f'http://localhost:5173/Thank-You-Email-Verification')
      
        return redirect('https://matrimony-livid.vercel.app/Thank-You-Email-Verification', code=302)
        # return jsonify({"message": f"Email {email} successfully verified!"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

class SendVerificationLink(Resource):
    def post(self):
        data = request.json
        user_email = data.get('email')
        if not user_email:
            return jsonify({"error": "Email is required"}), 400
        verificationLink = send_verification_email(user_email)
        print(verificationLink)
        return jsonify({"MessageVariable": verificationLink,"msg":"SUCCESS", "msgVal": "Verification Link Has Been Sent On Your Registered Email."})

api.add_resource(HelloWorld, '/HelloWorld')
api.add_resource(UserLogin, '/UserLogin')
api.add_resource(AddNewUser, '/AddUser')
api.add_resource(FetchAllUsers, '/GetClients')
api.add_resource(GetNewUserFormMasters, '/GetNewUserFormMasters')
api.add_resource(FetchMyProfile, '/FetchMyProfile')
api.add_resource(UpdateProfile, '/UpdateProfile')
api.add_resource(GetSingleProfileData, '/GetSingleProfileData')
api.add_resource(LogoutUser, '/LogoutUser')
api.add_resource(UpdateUserCollection, '/UpdateUserCollection')
api.add_resource(SendVerificationLink, '/SendVerificationLink')
api.add_resource(DeactivateAccount, '/DeactivateAccount')
api.add_resource(UpdatePreferences, '/UpdateExpectations')


if __name__ == "__main__":
    app.run(debug=True)