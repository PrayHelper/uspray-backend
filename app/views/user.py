from flask_restx import Namespace, Resource
from flask_restx import Namespace, Resource, fields
from flask import request, g, jsonify
import bcrypt
import datetime
import requests
import jwt

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

loginModel = user.model('Login', {
    'uid': fields.String(required=True, decription='user id'),
    'password': fields.String(required=True, decription='user password')
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
        return {'message': '회원가입에 성공하였습니다.'}


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


@user.route('/login', methods=['POST'])
class Login(Resource):
    @user.expect(loginModel)
    def post(self):
        """
        Login
        """
        content = request.json

        u = User.query.filter_by(uid=content['uid']).first

        if u is None:
            return { 'message' : '아이디가 존재하지 않습니다.' }
        
        if bcrypt.checkpw(content['password'].encode('UTF-8'), u.password):
            payload = {
                'uid': u.uid,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60 * 24)
            }
            token = jwt.encode(payload, "secret", algorithm="HS256")
            return { 'message' : '로그인에 성공하였습니다.', 'access_token': token }, 200
        else:
            return { 'message' : '비밀번호를 잘못 입력하였습니다.' }
