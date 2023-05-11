from flask_restx import Namespace, Resource, fields
from flask import request
import bcrypt
import datetime
import jwt
import os

from app.models.user import User
from app.utils.user import UserDTO, UserService
from app.decorators.login_required import login_required

user = Namespace('user', description='user test API')

userModel = user.model('User', {
    'id': fields.String(required=True, default='userid', description='user id'),
    'password': fields.String(required=True, default='password', description='user password'),
    'name': fields.String(required=True, default='name', description='user name'),
    'gender': fields.String(required=True, default='여', description='user gender'),
    'birth': fields.Date(required=True, default='2023-03-20', description='user birth'),
    'phone': fields.String(required=True, default='01012345678', description='user phone'),
})

loginModel = user.model('Login', {
    'id': fields.String(required=True, default='userid', decription='user id'),
    'password': fields.String(required=True, default='password', decription='user password')
})

findIdModel = user.model('FindId', {
    'name': fields.String(required=True, default='홍길동', description='user name'),
    'phone': fields.String(required=True, default='01012345678', description='user phone')
})

findPwModel = user.clone('FindPw', findIdModel, {
    'id': fields.String(required=True, default='userid', description='user id')
})

resetPasswordModel = user.model('ResetPassword', {
    'phone': fields.String(required=True, default='01012345678', description='user phone')
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
        user_dao = UserService.create_user(user_dto)
        return { 'message': '회원가입 되었습니다' }, 200


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
            access_payload = {
                'id': str(u.id),
                'access_token_exp': (datetime.datetime.utcnow() + datetime.timedelta(minutes=60 * 24)).isoformat()
            }
            access_token = jwt.encode(access_payload, os.getenv('SECRET_KEY'), algorithm="HS256")

            refresh_payload = {
                'id': str(u.id),
                'refresh_token_exp': (datetime.datetime.utcnow() + datetime.timedelta(minutes=60 * 24 * 60)).isoformat()
            }
            refresh_token = jwt.encode(refresh_payload, os.getenv('SECRET_KEY'), algorithm="HS256")
            return { 'access_token': access_token, 'refresh_token': refresh_token }, 200
        else:
            return { 'message' : '비밀번호를 잘못 입력하였습니다.' }, 400


@user.route('/find/id', methods=['POST'])
class FindId(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @user.expect(findIdModel)
    def post(self):
        """
        FindId
        """
        content = request.json
        u = User.query.filter_by(name=content['name'], phone=content['phone']).first()

        if u is None:
            return { 'message' : '유저가 존재하지 않습니다.' }, 400
        return { 'message': u.uid }, 200
    

@user.route('/find/password', methods=['POST'])
class FindPassword(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @user.expect(findPwModel)
    def post(self):
        """
        FindPassword
        """
        content = request.json

        u = User.query.filter_by(name=content['name'], phone=content['phone'], uid=content['id']).first()
        if u is None:
            return { 'message' : '유저가 존재하지 않습니다.' }, 400
        return { 'message': u.uid }, 200
    

@user.route('/reset/password', methods=['PUT'])
class ResetPassword(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @user.expect(loginModel)
    def put(self):
        """
        ResetPassword
        """
        content = request.json
        UserService.update_password(content['id'], content['password'])
        return { 'message' : '비밀번호가 변경되었습니다.' }, 200
    

@user.route('/reset/phone', methods=['PUT'])
class ResetPhone(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @user.expect(resetPasswordModel)
    @login_required
    def put(self):
        """
        ResetPhone
        """
        content = request.json
        UserService.update_phone(content['phone'])
        return { 'message' : '전화번호가 변경되었습니다.' }, 200