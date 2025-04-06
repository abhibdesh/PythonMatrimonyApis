from flask import Flask, redirect, request, jsonify, session
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import requests
from Admin import GetPaymentSettlement,SettlePaymentOwner,GetAggregateAmount,DownloadMyPaymentSettlement,FetchAdminDashboard,FetchDashboardData, VerifyAccount,FetchAllUsersAdmin,PromoteToAdmin,GetAllReferenceCodes,GetMyReferences
from itsdangerous import URLSafeTimedSerializer
from PaymentApi import GetContactDetails,GenerateQRCode,GetMyPayments,MarkPaymentDone,GetPaymentsToApprove,ApprovePayment
from pymongo import MongoClient
from UserApis import MySavedProfiles,GetMyContacts,ChangePassword,ForgotPassword,GetProfilePicture,LogOutFromPreviousDevice,UserLogin,UpdatePreferences, AddNewUser,DeactivateAccount, FetchAllUsers, FetchMyProfile, LogoutUser, UpdateProfile, GetSingleProfileData
from UpdateExistingRecords import TruncateAllCollections,UpdateUserCollection
from GetMasters import GetNewUserFormMasters
from CronJobs import CheckActiveUsers , CheckPaymentInfo
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

META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN','EAAN1yyNSqyIBO5e6SKy7ciDW0djMhSiSnSoZBZA4KNmJHiZCK9YMY4DcXei1TWmBA319mW4uZA5zj1K0ESk7iXUWWM8SvY04zSHeGcNDlMEuvL8ZCpQilE4UZAZCt9ljZAGXqVuuasfpZCO1GTIrpTEMyrAdPqkm4pNP4bPXZCkujGWs9L6mJecplcZCrxrKrMFAwDHBND0m9pa0aUEffqLu9hhMxZB97X9gezkeGDYZD')
META_PHONE_NUMBER_ID = os.getenv('META_PHONE_NUMBER_ID','607370069123259')
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{META_PHONE_NUMBER_ID}/messages"

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

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == META_ACCESS_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("Incoming:", data)

    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    user_number = message["from"]
                    message_body = message["text"]["body"].strip().lower()
                    # Example: Trigger OTP reply on "verify" keyword
                    if "verify" in message_body:
                        send_otp_to_user(user_number,generate_otp())
    return "OK", 200

def generate_otp():
    return random.randint(100000, 999999)

def send_otp_to_user(phone_number, otp):
    # TODO: integrate with WhatsApp Cloud API to send OTP
    print(f"Sending OTP to {phone_number}...")
    url = f"https://graph.facebook.com/v19.0/{META_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": f"Your OTP is: {otp}"
        }
        
    }

    response = requests.post(url, json=data, headers=headers)
    return response.status_code == 200
    # Implement the actual POST request here to Meta API
    
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
api.add_resource(ForgotPassword, '/ForgotPassword')
api.add_resource(ChangePassword, '/ChangePassword')
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
api.add_resource(FetchAdminDashboard, '/FetchAdminDashboard')
api.add_resource(GenerateQRCode, '/GenerateQRCode')
api.add_resource(CheckActiveUsers, '/CheckActiveUsers')
api.add_resource(MarkPaymentDone, '/MarkPaymentDone')
api.add_resource(LogOutFromPreviousDevice, '/LogOutFromPreviousDevice')
api.add_resource(ApprovePayment, '/ApprovePayment')
api.add_resource(GetProfilePicture, '/GetProfilePicture')
api.add_resource(GetPaymentsToApprove, '/GetPaymentsToApprove')
api.add_resource(PromoteToAdmin,"/PromoteToAdmin")
api.add_resource(GetAllReferenceCodes,"/GetAllReferenceCodes")
api.add_resource(GetMyReferences,"/GetMyReferences")
api.add_resource(GetContactDetails,"/GetContactDetails")
api.add_resource(GetMyContacts,"/GetMyContacts")
api.add_resource(MySavedProfiles,"/MySavedProfiles")
api.add_resource(TruncateAllCollections,"/TruncateAllCollections")
api.add_resource(CheckPaymentInfo,"/CheckPaymentInfo")
api.add_resource(DownloadMyPaymentSettlement,"/DownloadMyPaymentSettlement")
api.add_resource(GetAggregateAmount,"/GetAggregateAmount")
api.add_resource(GetPaymentSettlement,"/GetPaymentSettlement")
api.add_resource(SettlePaymentOwner,"/SettlePaymentOwner")




if __name__ == "__main__":
    app.run(debug=True)