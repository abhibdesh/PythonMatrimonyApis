from flask import Flask, redirect, request, jsonify, session
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import requests
from Admin import GetUserCommunityList,GetUserWithoutCommunity,AddAsAdmin,GetPaymentSettlement,SettlePaymentOwner,GetAggregateAmount,DownloadMyPaymentSettlement,FetchAdminDashboard,FetchDashboardData, VerifyAccount,FetchAllUsersAdmin,PromoteToAdmin,GetAllReferenceCodes,GetMyReferences
from itsdangerous import URLSafeTimedSerializer
from PaymentApi import GetContactDetails,GenerateQRCode,GetMyPayments,MarkPaymentDone,GetPaymentsToApprove,ApprovePayment
from pymongo import MongoClient
from UserApis import GetImagesById,DeleteImages,SetProfileImage,GetImages,UploadImages,VerifyOPT,MySavedProfiles,GetMyContacts,ChangePassword,ForgotPassword,GetProfilePicture,LogOutFromPreviousDevice,UserLogin,UpdatePreferences, AddNewUser,DeactivateAccount, FetchAllUsers, FetchMyProfile, LogoutUser, UpdateProfile, GetSingleProfileData
from UpdateExistingRecords import TruncateAllCollections,UpdateUserCollection
from GetMasters import GetNewUserFormMasters
from CronJobs import CheckActiveUsers , CheckPaymentInfo
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import os
import logging
import pytz
import random
import time


app = Flask(__name__)
api = Api(app)
CORS(app
    #  , resources={r"/*": {
    #     "origins": "http://localhost:5173"
    #                      , "allow_headers": "Authorization"
    #                       }
    #               }
     )

mongoURI = os.getenv('MONGO_URL','')
databse = os.getenv('DATABSE',"")
client = MongoClient(mongoURI)
db = client.get_database(databse)

app.config['JWT_SECRET_KEY'] = os.getenv('SECERT_KEY','')
serializer = URLSafeTimedSerializer(os.getenv('SECERT_KEY',''))

META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN','')
META_PHONE_NUMBER_ID = os.getenv('META_PHONE_NUMBER_ID','607370069123259')
WHATSAPP_API_URL = f"https://graph.facebook.com/v19.0/{META_PHONE_NUMBER_ID}/messages"

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1) 

jwt = JWTManager(app)
logger = logging.getLogger(__name__)

local_timezone = pytz.timezone('Asia/Kolkata')  
now_local_tz = datetime.now(local_timezone)
otp_cache = {}
MAX_OTPS = 3
WINDOW_SECONDS = 600  # 10 minutes

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
      
        return redirect('THANKYOUPAGELINK', code=302)
        # return jsonify({"message": f"Email {email} successfully verified!"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 400

@app.route("/webhook", methods=["GET"])
def verify():
    print("WEBHOOK get")
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == META_ACCESS_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def receive_message():
    print("WEBHOOK post")
    data = request.get_json()
    print("Incoming:", data)

    if data.get("object") == "whatsapp_business_account":
        for entry in data.get("entry", []):
            print("entry:" )
            print(entry)
            for change in entry.get("changes", []):
                print("change:")
                print(change)
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    print("message:")
                    print(message)
                    user_number = message["from"]
                    message_body = message["text"]["body"].strip().lower()
                    print("message_body")
                    print(message_body)
                    # Example: Trigger OTP reply on "verify" keyword
                    if "verify" in message_body:
                        if can_send_otp(user_number):
                            otp = generate_otp()
                            send_otp_to_user(user_number,str(otp))
                        else:
                            print(f"Rate limit hit for {user_number}")
    return "OK", 200

def can_send_otp(phone_number):
    now = time.time()
    if phone_number not in otp_cache:
        otp_cache[phone_number] = []

    recent = [t for t in otp_cache[phone_number] if now - t < WINDOW_SECONDS]
    otp_cache[phone_number] = recent

    if len(recent) < MAX_OTPS:
        otp_cache[phone_number].append(now)
        return True
    return False

def generate_otp():
    return random.randint(100000, 999999)

def send_otp_to_user(phone_number, otp):
    print("OTP get")
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
            "body": f"Your OTP is: {otp}.This OTP will be valid for 1 hour. Do not share this OTP with anyone."
        }
        
    }

    response = requests.post(url, json=data, headers=headers)
    save_otp(phone_number,otp)   
    print("Meta response:", response.status_code, response.text)  # ADD THIS
    return response.status_code == 200
    # Implement the actual POST request here to Meta API
    
def save_otp(phone,otp):
    print("save Otp")
    collection = db.get_collection("OTPValidations")
    validTill = datetime.now() + relativedelta(hours=1)
    collection.insert_one({
        "UserPhoneNumber" : str(phone),
        "OTP" : str(otp),
        "IsValid" : True,
        "ValidTill":validTill,
        "created_at": datetime.now()
    })
    
    
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
api.add_resource(VerifyOPT, '/VerifyOPT')
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
api.add_resource(AddAsAdmin,"/AddAsAdmin")
api.add_resource(GetUserWithoutCommunity,"/GetUserWithoutCommunity")
api.add_resource(GetUserCommunityList,"/GetUserCommunityList")
api.add_resource(UploadImages,"/UploadImages")
api.add_resource(GetImages,"/GetImages")
api.add_resource(DeleteImages,"/DeleteImages")
api.add_resource(SetProfileImage,"/SetProfileImage")
api.add_resource(GetImagesById,"/GetImagesById")


if __name__ == "__main__":
    app.run(debug=True)