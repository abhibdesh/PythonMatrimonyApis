from flask import Flask, redirect, request, jsonify, session
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from Admin import FetchDashboardData, VerifyAccount,FetchAllUsersAdmin
from itsdangerous import URLSafeTimedSerializer
from PaymentApi import GenerateQRCode,GetMyPayments,MarkPaymentDone,GetPaymentsToApprove,ApprovePayment
from pymongo import MongoClient
from UserApis import LogOutFromPreviousDevice,UserLogin,UpdatePreferences, AddNewUser,DeactivateAccount, FetchAllUsers, FetchMyProfile, LogoutUser, UpdateProfile, GetSingleProfileData
from UpdateExistingRecords import UpdateUserCollection
from GetMasters import GetNewUserFormMasters
from CronJobs import CheckActiveUsers
from datetime import datetime, timedelta
import json
import os
import logging
import pytz


app = Flask(__name__)
api = Api(app)
CORS(app
    #  , resources={r"/*": {
    #     "origins": "http://localhost:5173"
    #                      , "allow_headers": "Authorization"
    #                       }
    #               }
     )

mongoURI = os.getenv('MONGO_URL','mongodb+srv://abhibdesh:k6fEWav4Dkc1rQzn@mat.podj9wc.mongodb.net/?retryWrites=true&w=majority&appName=Mat')
databse = os.getenv('DATABSE',"Matrimony")
client = MongoClient(mongoURI)
db = client.get_database(databse)

app.config['JWT_SECRET_KEY'] = os.getenv('SECERT_KEY','asdfghjklpoiuytrewfgvbndcksdhfjgjhejbdsjbcsbh')
serializer = URLSafeTimedSerializer(os.getenv('SECERT_KEY','asdfghjklpoiuytrewfgvbndcksdhfjgjhejbdsjbcsbh'))
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)
logger = logging.getLogger(__name__)

local_timezone = pytz.timezone('Asia/Kolkata')  
now_local_tz = datetime.now(local_timezone)

class HelloWorld(Resource):
    def get(self):
        try:
            return {"hello":"world"}
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
        collection.update_one({"UserEmail":email},{"$set":{"isEmailVerified":True,"lastActivity":datetime.now()}})
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
        collection = db.get_collection("User")
        collection.update_one({
            "UserEmail":user_email
        },{
            "$set":{
                "lastActivity": str(now_local_tz)
            }
        })
        if not user_email:
            return jsonify({"error": "Email is required"}), 400
        verificationLink = send_verification_email(user_email)
        print(verificationLink)
        return jsonify({"MessageVariable": verificationLink,"msg":"SUCCESS", "msgVal": "Verification Link Has Been Sent On Your Registered Email."})

api.add_resource(HelloWorld, '/HelloWorld')
api.add_resource(UserLogin, '/UserLogin')
api.add_resource(AddNewUser, '/AddUser')
api.add_resource(FetchAllUsers, '/GetClients')
api.add_resource(FetchDashboardData, '/FetchDashboardData')
api.add_resource(VerifyAccount, '/VerifyAccount')
api.add_resource(GetNewUserFormMasters, '/GetNewUserFormMasters')
api.add_resource(FetchMyProfile, '/FetchMyProfile')
api.add_resource(UpdateProfile, '/UpdateProfile')
api.add_resource(GetSingleProfileData, '/GetSingleProfileData')
api.add_resource(LogoutUser, '/LogoutUser')
api.add_resource(UpdateUserCollection, '/UpdateUserCollection')
api.add_resource(SendVerificationLink, '/SendVerificationLink')
api.add_resource(DeactivateAccount, '/DeactivateAccount')
api.add_resource(UpdatePreferences, '/UpdateExpectations')
api.add_resource(GetMyPayments, '/GetMyPayments')
api.add_resource(FetchAllUsersAdmin, '/FetchAllUsersAdmin')
api.add_resource(GenerateQRCode, '/GenerateQRCode')
api.add_resource(CheckActiveUsers, '/CheckActiveUsers')
api.add_resource(MarkPaymentDone, '/MarkPaymentDone')
api.add_resource(LogOutFromPreviousDevice, '/LogOutFromPreviousDevice')
api.add_resource(ApprovePayment, '/ApprovePayment')
api.add_resource(GetPaymentsToApprove, '/GetPaymentsToApprove')

if __name__ == "__main__":
    app.run(debug=True)