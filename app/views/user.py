from flask_restx import Namespace, Resource
from flask_restx import Namespace, Resource, fields
from flask import request, g
import bcrypt
import datetime
import requests 

user = Namespace('user', description='user test API')

userModel = user.model('User', {
    'uid': fields.String(required=True, description='user id'),
    'password': fields.String(required=True, description='user password'),
    'name': fields.String(required=True, description='user name'),
    'gender': fields.String(required=True, description='user gender'),
    'birth': fields.Date(required=True, description='user birth'),
    'phone': fields.String(required=True, description='user phone'),
})

@user.route('/signup', methods=['POST'])
class SignUp(Resource):
    @user.expect(userModel)
    def post(self):
        """
        Signup
        """
        content = request.json
        return {'message': 'Hello World'}