from flask_restx import Namespace, Resource, fields
from flask import request, g
import bcrypt
import datetime
import jwt
import os

from app.models.user import User
from app.utils.user import UserDTO, UserService
from app.decorators.login_required import login_required
from app.utils.error_handler import InvalidTokenError

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


checkPasswordModel = user.model('CheckPassword', {
    'password': fields.String(required=True, default='password', description='user password')
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
        UserService.create_user(user_dto)
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
        if u.deleted_at is not None:
            return { 'message' : '탈퇴한 회원입니다.' }, 400
        if bcrypt.checkpw(content['password'].encode('UTF-8'), u.password.encode('UTF-8')):
            access_payload = {
                'id': str(u.id),
                'access_token_exp': (datetime.datetime.now() + datetime.timedelta(minutes=60*24)).isoformat()
            }
            access_token = jwt.encode(access_payload, os.getenv('SECRET_KEY'), algorithm="HS256")

            refresh_payload = {
                'id': str(u.id),
                'refresh_token_exp': (datetime.datetime.now() + datetime.timedelta(minutes=60*24*60)).isoformat()
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
    

@user.route('/reset/password', methods=['PUT'])
class ResetPassword(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @login_required
    @user.expect(checkPasswordModel)
    def put(self):
        """
        ResetPassword
        """
        content = request.json
        UserService.update_password(content['password'])
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
    
    
@user.route('/check/pw', methods=['POST'])
class CheckPassword(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @user.expect(checkPasswordModel)
    @login_required
    def post(self):
        """
        CheckPassword
        """
        content = request.json
        user = g.user
        if bcrypt.checkpw(content['password'].encode('UTF-8'), user.password.encode('UTF-8')):
            return { 'message' : True }, 200
        else:
            return { 'message' : False }, 200
    


@user.route('/withdrawal', methods=['DELETE'])
class Withdrawal(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @login_required
    def delete(self):
        """
        Withdrawal
        """
        UserService.delete_user()
        return { 'message' : '회원탈퇴 되었습니다.' }, 200
    

@user.route('/token', methods=['GET'])
class Token(Resource):
    def get(self):
        """
        AuthToken
        """
        access_token = request.headers.get("Authorization")
        
        if access_token:
            try:
                payload = jwt.decode(access_token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
                user_id = payload['id']
                if 'access_token_exp' in payload:
                    access_token_exp = payload['access_token_exp']
                    if datetime.datetime.fromisoformat(access_token_exp) < datetime.datetime.now():
                        raise InvalidTokenError("access token expired", 403, 403)
                    else:
                        u = User.query.filter_by(id=user_id).first()
                        if u is not None and u.deleted_at is None:
                            g.user_id = user_id
                            g.user = u
                        else:
                            g.user = None
                            raise InvalidTokenError("user not found")
                elif 'refresh_token_exp' in payload:
                    refresh_token_exp = payload['refresh_token_exp']
                    if datetime.datetime.fromisoformat(refresh_token_exp) < datetime.datetime.now():
                        raise InvalidTokenError("refresh token expired", 401, 401)
                    else:
                        payload = {
                            'id': user_id,
                            'access_token_exp': (datetime.datetime.now() + datetime.timedelta(minutes=60 * 24)).isoformat()
                        }
                        token = jwt.encode(payload, os.getenv('SECRET_KEY'), algorithm="HS256")
                        return { 'access_token': token }, 200
            except jwt.InvalidTokenError:
                raise InvalidTokenError("invalid token")
            return { 'message' : 'token is valid' }, 200
        else:
            raise InvalidTokenError("token not found")

