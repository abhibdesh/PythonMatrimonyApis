from flask import Flask, request,jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import firebase_admin
from firebase_admin import credentials
from UserApis import UserLogin, AddNewUser, FetchAllUsers
import secrets
import json
from datetime import timedelta
from jwt import DecodeError
from jwt.exceptions import PyJWTError as DecodeError



app = Flask(__name__)
api = Api(app)
CORS(app
    #  , resources={r"/*": {"origins": "http://localhost:5173"}}
     )
service_account_key = './Config/FirebaseCreds.json'
with open('./Config/Creds.json') as f:
    config = json.load(f)
    mongoURI = config['uri']
cred = credentials.Certificate(service_account_key)
firebase_admin.initialize_app(cred)
app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(32)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)


class HelloWorld(Resource):
    def get(self):
        try:
            # current_user = get_jwt_identity()
            return {"hello":"wrold"}
        except Exception as e:
            print(e)
            return {"data": "HelloWorld!!!"}


api.add_resource(HelloWorld, '/HelloWorld')
api.add_resource(UserLogin, '/UserLogin')
api.add_resource(AddNewUser, '/AddUser')
api.add_resource(FetchAllUsers, '/GetClients')






if __name__ == "__main__":
    app.run(debug=True)
