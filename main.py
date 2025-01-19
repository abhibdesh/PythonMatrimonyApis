from flask import Flask, request, jsonify, url_for
from flask_mail import Mail, Message
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import firebase_admin
from firebase_admin import credentials
from UserApis import UserLogin, AddNewUser, FetchAllUsers, FetchMyProfile, LogoutUser, UpdateProfile, GetSingleProfileData
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
cred = credentials.Certificate(service_account_key)
firebase_admin.initialize_app(cred)
# app.config['JWT_SECRET_KEY'] = os.getenv('SECERT_KEY')
app.config['JWT_SECRET_KEY'] = "asdfghjklpoiuytrewfgvbndcksdhfjgjhejbdsjbcsbh" # Dummy Key 
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = "vivaahbandhan@aol.com"
app.config['MAIL_PASSWORD'] = 'YJ5G4mqWRXCJ@kz'
app.config['MAIL_DEFAULT_SENDER'] = ('Vivaah Bandhan', 'vivaahbandhan@aol.com')

mail = Mail(app)

class HelloWorld(Resource):
    def get(self):
        try:
            # current_user = get_jwt_identity()
            return {"hello":"wrold"}
        except Exception as e:
            print(e)
            return {"data": "HelloWorld!!!"}


# Generate verification token
def generate_verification_token(email):
    """Generate a JWT token for email verification."""
    return create_access_token(identity=email, expires_delta=timedelta(hours=24))

# Send verification email
def send_verification_email(user_email):
    print("JJJIJIJIJIJIJIJIJIJIJ")
    token = generate_verification_token(user_email)
    
    print(token)
    verification_url = url_for('verify_email', token=token, _external=True)
    print(verification_url)
    msg = Message(
        subject="Email Verification For Vivah Bandhan",
        recipients=[user_email],
        body=f"Click the link to verify your email: {verification_url}"
    )
    msg.body = msg.body.encode('utf-8').decode('utf-8')
    print(msg)
    msg.charset = 'utf-8'
    mail.send(msg)

# Email verification route
@app.route('/verify-email', methods=['GET'])
def verify_email():
    """Verify the email using the token."""
    token = request.args.get('token')
    if not token:
        return jsonify({"error": "Token is required"}), 400

    try:
        # Decode and verify the token
        email = get_jwt_identity()  # Extract identity from the token
        # Mark email as verified in the database
        return jsonify({"message": f"Email {email} successfully verified!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Resource for sending emails
class SendMail(Resource):
    def post(self):
        data = request.json
        user_email = data.get('email')
        if not user_email:
            return jsonify({"error": "Email is required"}), 400
        send_verification_email(user_email)
        return jsonify({"message": "Verification email sent!"}), 200

# Register API resources
api.add_resource(UserLogin, '/UserLogin')
api.add_resource(AddNewUser, '/AddUser')
api.add_resource(FetchAllUsers, '/GetClients')
api.add_resource(GetNewUserFormMasters, '/GetNewUserFormMasters')
api.add_resource(FetchMyProfile, '/FetchMyProfile')
api.add_resource(UpdateProfile, '/UpdateProfile')
api.add_resource(GetSingleProfileData, '/GetSingleProfileData')
api.add_resource(LogoutUser, '/LogoutUser')
api.add_resource(UpdateUserCollection, '/UpdateUserCollection')
api.add_resource(SendMail, '/VerifyEmailId')

if __name__ == "__main__":
    app.run(debug=True)