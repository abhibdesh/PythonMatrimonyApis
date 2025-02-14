from flask import request, jsonify
from flask_restful import Resource
from bcrypt import gensalt, checkpw, hashpw
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from pymongo import MongoClient
import json
from jwt import DecodeError
from jwt.exceptions import PyJWTError as DecodeError
import urllib.parse
import qrcode
import io
import base64
from datetime import datetime
from pymongo import DESCENDING
from dateutil.relativedelta import relativedelta
import os
import pytz

mongoURI = os.getenv('MONGO_URL','mongodb+srv://abhibdesh:k6fEWav4Dkc1rQzn@mat.podj9wc.mongodb.net/?retryWrites=true&w=majority&appName=Mat')
databse = os.getenv('DATABSE',"Matrimony")
client = MongoClient(mongoURI)
db = client.get_database(databse)

local_timezone = pytz.timezone('Asia/Kolkata')  
now_local_tz = datetime.now(local_timezone)

        
class GetMyPayments(Resource):
    def post(self):
        userId = request.json["userId"]
        today_date = datetime.now() 
        print("userIduserIduserIduserIduserIduserIduserIduserIduserIduserId")
        print(userId)
        print("userIduserIduserIduserIduserIduserIduserIduserIduserIduserId")
        collection = db.get_collection("User")
        collection.update_one({ "UserId": int(userId)},{
            "$set":{
            "lastActivity": str(now_local_tz)
            }
        })
        result = db.User.aggregate([
            {
                "$match": {  
                    "UserId": int(userId)
                }
            },
            {
                "$lookup": { 
                    "from": "PaymentInfo",
                    "localField": "UserId",
                    "foreignField": "UserId",
                    "as": "payments",
                    "pipeline": [
                        {
                            "$addFields": {
                                "isActive": { "$gt": ["$ValidTill", today_date] }  
                            }
                        },
                        { "$sort": { "CreatedDate": DESCENDING } },  
                        { "$project": { "_id": 0 }}  
                    ]
                }
            },
            {
                "$project": {
                    "_id": 0,  
                    "payments": 1  
                }
            }
        ])            

        paymentData = []
        hasActivePlan = False 

        for doc in result:
            for payment in doc.get("payments", []):
                if payment.get("isActive"): 
                    hasActivePlan = True
            paymentData.append(doc)

        return jsonify({
            "message": "success",
            "data": paymentData,
            "hasActivePlan": hasActivePlan  
        })


class GenerateQRCode(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        payer_name = request.json["userName"]
        PlanTimeSelected = request.json["PlanTimeSelected"]
        ProfileCount = request.json["ProfileCount"]
        UserId = request.json["UserId"]
        upi_id = "abhibdesh@okaxis"
        amount = "0.00"
        # txn_id = "TXN123456"
        txn_id = "TXN123456"
        # note = "Payment for Order #123"
        note = "Payment for Vivaah Bandhan "
        print (now_local_tz)
        print("PlanTimeSelected")
        print(PlanTimeSelected)
        print("____________________")    
        print("ProfileCount")        
        print(ProfileCount)
        collection = db.get_collection("User")
        collection.update_one({
            "UserId":int(UserId)
        },{
            "$set":{
                "lastActivity":str(now_local_tz)
            }
        })
        
        paymentCollection = db.get_collection("PaymentInfo")
        if PlanTimeSelected == "1" and ProfileCount == "10":
            amount = "499.00"
            validTill = datetime.now() + relativedelta(months=1)
        if PlanTimeSelected == "1" and ProfileCount == "20":
            amount = "899.00"
            validTill = datetime.now() + relativedelta(months=1)
        if PlanTimeSelected == "1" and ProfileCount == "30":
            amount = "1299.00"
            validTill = datetime.now() + relativedelta(months=1)
        if PlanTimeSelected == "1" and ProfileCount == "Unlimited":
            amount = "1599.00"
            validTill = datetime.now() + relativedelta(months=1)

        if PlanTimeSelected == "3" and ProfileCount == "10":
            amount = "899.00"
            validTill = datetime.now() + relativedelta(months=3)
        if PlanTimeSelected == "3" and ProfileCount == "20":
            amount = "1299.00"
            validTill = datetime.now() + relativedelta(months=3)
        if PlanTimeSelected == "3" and ProfileCount == "30":
            amount = "1599.00"
            validTill = datetime.now() + relativedelta(months=3)
        if PlanTimeSelected == "3" and ProfileCount == "Unlimited":
            amount = "1999.00"
            validTill = datetime.now() + relativedelta(months=3)

        if PlanTimeSelected == "6" and ProfileCount == "10":
            amount = "1299.00"
            validTill = datetime.now() + relativedelta(months=6)
        if PlanTimeSelected == "6" and ProfileCount == "20":
            amount = "1599.00"
            validTill = datetime.now() + relativedelta(months=6)
        if PlanTimeSelected == "6" and ProfileCount == "30":
            amount = "1999.00"
            validTill = datetime.now() + relativedelta(months=6)
        if PlanTimeSelected == "6" and ProfileCount == "Unlimited":
            amount = "2499.00"
            validTill = datetime.now() + relativedelta(months=6)

        if PlanTimeSelected == "9" and ProfileCount == "10":
            amount = "1599.00"
            validTill = datetime.now() + relativedelta(months=9)
        if PlanTimeSelected == "9" and ProfileCount == "20":
            amount = "1999.00"
            validTill = datetime.now() + relativedelta(months=9)
        if PlanTimeSelected == "9" and ProfileCount == "30":
            amount = "2499.00"
            validTill = datetime.now() + relativedelta(months=9)
        if PlanTimeSelected == "9" and ProfileCount == "Unlimited":
            amount = "3999.00"
            validTill = datetime.now() + relativedelta(months=9)

        if PlanTimeSelected == "1Y":
            amount = "4999.00"
            validTill = datetime.now() + relativedelta(years=1)

         
        a = str(now_local_tz).replace("-","").replace(":","").replace(" ","").split(".")[0]
        today = datetime.now(local_timezone).date() 
        start_of_day = datetime(today.year, today.month, today.day, 0, 0, 0, 0, tzinfo=local_timezone)
        end_of_day = datetime(today.year, today.month, today.day, 23, 59, 59, 999999, tzinfo=local_timezone)
        count = paymentCollection.count_documents({"CreatedDate": {"$gte": start_of_day, "$lte": end_of_day}})
        print(count)
        transactionId = ""
        if count >= 0 and count < 10: transactionId = a+"0000"+str(count)
        if count > 9 and count < 100 : transactionId = a+"000"+str(count)
        if count > 99 and count < 1000 : transactionId = a+"00"+str(count)

        if ProfileCount == "Unlimited":
            ProfileCount = 0
        else:
            ProfileCount = int(ProfileCount)

        paymentCollection.insert_one(
            {
                "PlanTimeSelected":PlanTimeSelected,
                "ProfileCount":ProfileCount,
                "CreatedDate" : now_local_tz,
                "IsPaymentDone":0,
                "IsApproved":0,
                "amount":amount,
                "ValidTill":validTill,
                "transactionId" : transactionId,
                "UserId": int(UserId),
                "UserEmail" : current_user,
                "UserPaid":True,
                "TotalProfilesView": 0,
                "LimitExhausted":False,
                "savedProfiles" : []
            }
        )

        note = note + " PlanTimeSelected "+PlanTimeSelected +" ProfileCount "+ str(ProfileCount)
        upi_link = f"upi://pay?pa={upi_id}&pn={urllib.parse.quote(payer_name)}&mc=&tid={transactionId}&tr={transactionId}&tn={urllib.parse.quote(note)}&am={amount}&cu=INR"
        img_io = io.BytesIO()
        qr = qrcode.make(upi_link)
        print(qr)
        qr.save(img_io, format="PNG")
        img_io.seek(0)
        print("UPI Payment Link:", upi_link)
        baseimg = base64.b64encode(img_io.getvalue()).decode('utf-8')

        return jsonify({"message":"success","qr":baseimg, "txn_id":transactionId})
    

class MarkPaymentDone(Resource):
    @jwt_required()
    def post(self):
        txn_id = request.json["txn_id"]
        print(txn_id)
        try:
        
            paymentCollection = db.get_collection("PaymentInfo")
            paymentCollection.update_one({"transactionId":txn_id},
                                        {
                                            "$set":{
                                                "IsPaymentDone":1
                                            }
                                        })
            return jsonify({"message":"success","data":"Your Payment has been submitted for approval."})
        except Exception as e:
            print(f"Error fetching users: {e}")
            error_collection = db.get_collection('ErrorLogs')
            error_collection.insert_one({
                "Method": "MarkPaymentDone",
                "Exception": str(e),
                "Time": datetime.now()
            })
            return jsonify({"message": "Failure", "data": "Something Went Wrong"})

class GetPaymentsToApprove(Resource):
    def post(self):
        print("Hello")

class ApprovePayment(Resource):
    def post(self):
        print("Hello")