from flask_restx import Namespace, Resource, fields
from flask import request
import bcrypt
import datetime
import jwt
import os

from app.models import db
from app.models.user import User
from app.utils.user import UserDTO, UserDAO

user = Namespace('user', description='user test API')

userModel = user.model('User', {
    'id': fields.String(required=True, default='userid', description='user id'),
    'password': fields.String(required=True, default='password', description='user password'),
    'name': fields.String(required=True, default='name', description='user name'),
    'gender': fields.String(required=True, default='여', description='user gender'),
    'birth': fields.Date(required=True, default='2023-03-20', description='user birth'),
    'phone': fields.String(required=True, default='01011112222', description='user phone'),
})

loginModel = user.model('Login', {
    'id': fields.String(required=True, default='userid', decription='user id'),
    'password': fields.String(required=True, default='password', decription='user password')
})

@user.route('/signup', methods=['POST'])
class SignUp(Resource):
    @user.expect(userModel)
    def post(self):
        """
        Signup
        """
        content = request.json
        user_dto = UserDTO(
            uid=content['id'],
            password=content['password'],
            name=content['name'],
            gender=content['gender'],
            birth=content['birth'],
            phone=content['phone']
        )
        user_dao = UserDAO.create_user(user_dto)
        payload = {
            'id': str(user_dao.id),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60 * 24)
        }
        token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm="HS256")
        return { 'access_token': token }, 200


@user.route('/dup_check/<string:id>', methods=['GET'])
class IdDupCheck(Resource):
    @user.doc(params={'id': 'uos920'})
    def get(self, id):
        """
        IdDupCheck
        """
        dupUserId = User.query.filter_by(uid=id).first()
        if dupUserId is None:
            return { 'dup': False }, 200
        return { 'dup' : True }, 200


@user.route('/login', methods=['POST'])
class Login(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @user.expect(loginModel)
    def post(self):
        """
        Login
        """
        content = request.json

        u = User.query.filter_by(uid=content['id']).first()

        if u is None:
            return { 'message' : '아이디가 존재하지 않습니다.' }, 400
        
        if bcrypt.checkpw(content['password'].encode('UTF-8'), u.password.encode('UTF-8')):
            payload = {
                'id': str(u.id),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60 * 24)
            }
            token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm="HS256")
            return { 'access_token': token }, 200
        else:
            return { 'message' : '비밀번호를 잘못 입력하였습니다.' }, 400
