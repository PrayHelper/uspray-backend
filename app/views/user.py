from flask_restx import Namespace, Resource
from flask_restx import Namespace, Resource, fields
from flask import request, g, jsonify
import bcrypt
import datetime
import requests

from app import db
from app.models.user import User
from app.dto.user import UserDTO 

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
        u = UserDTO.create_user(
            uid=content['uid'],
            password=content['password'],
            name=content['name'],
            gender=content['gender'],
            birth=content['birth'],
            phone=content['phone']
        )
        print(u)
        return {'message': 'Hello World'}

@user.route('/dup_check', methods=['GET'])
class IdDupCheck(Resource):
    @user.doc(params={'uid': 'uid'})
    def get(self):
        """
        IdDupCheck
        """
        uid = request.args.get('uid')
        dupUserId = User.query.filter_by(uid=uid).first()
        if dupUserId is None:
            return jsonify({'dup' : False})
        return jsonify({'dup' : True})
