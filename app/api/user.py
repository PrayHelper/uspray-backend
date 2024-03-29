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
    'gender': fields.String(required=False, default='여자', description='user gender'),
    'birth': fields.Date(required=False, default='2023-03-20', description='user birth'),
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

checkInformModel = user.model('CheckInform', {
    'id': fields.String(required=True, default='userid', description='user id'),
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

deviceTokenModel = user.model('DeviceToken', {
    'device_token': fields.String(required=True, default='device_token', description='device token')
})

withdrawalModel = user.model('Withdrawal', {
    'reason_id': fields.List(fields.Integer, required=True, default=[1, 2], description='reason id'),
    'etc': fields.String(required=False, default='기타', description='etc')
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
            gender=content['gender'] if 'gender' in content else None,
            birth=content['birth'] if 'birth' in content else None,
            phone=content['phone']
        )
        return UserService.create_user(user_dto)


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
            return { 'access_token': access_token, 'refresh_token': refresh_token, 'user_id': u.uid }, 200
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
    
@user.route('/find/password', methods=['PUT'])
class FindPassword(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @user.doc(params={'token': {'description': 'token'}})
    @user.expect(checkPasswordModel)
    def put(self):
        """
        FindPassword
        """
        token = request.args.get('token')
        if token is None:
            return { 'message' : 'token을 입력해주세요.' }, 400

        u = User.query.filter_by(reset_pw=token).first()
        if u is None:
            return { 'message' : '인증에 실패했습니다.' }, 400
        
        content = request.json
        UserService.find_password(u, content['password'])
        return { 'message' : '비밀번호가 변경되었습니다.' }, 200


@user.route('/check/inform', methods=['POST'])
class CheckInform(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @user.expect(checkInformModel)
    def post(self):
        """
        CheckInform
        """
        content = request.json
        u = User.query.filter_by(uid=content['id'], phone=content['phone']).first()

        if u is None:
            return { 'message' : False }, 200
        else:
            token = UserService.reset_password(u)
            return { 'message': True, 'token': token }, 200


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
    @user.expect(withdrawalModel)
    @login_required
    def delete(self):
        """
        Withdrawal
        """
        content = request.json
        UserService.delete_user(content)
        return { 'message' : '회원탈퇴 되었습니다.' }, 200
    

@user.route('/token', methods=['GET'])
class Token(Resource):
    def get(self):
        """
        AuthToken
        """
        access_token = request.headers.get("Authorization")
        
        if access_token and access_token != "undefined":
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


@user.route('/notification/<int:notification_id>/enable', methods=['PUT'])
class NotificationEnable(Resource):
    @login_required
    def put(self, notification_id):
        """
        NotificationEnable
        """
        UserService.enable_notification(notification_id)
        return { 'message' : '알림이 활성화 되었습니다.' }, 200
    

@user.route('/notification/<int:notification_id>/disable', methods=['PUT'])
class NotificationDisable(Resource):
    @login_required
    def put(self, notification_id):
        """
        NotificationDisable
        """
        UserService.disable_notification(notification_id)
        return { 'message' : '알림이 비활성화 되었습니다.' }, 200
    

@user.route('/notifications', methods=['GET'])
class NotificationList(Resource):
    @login_required
    def get(self):
        """
        UserNotificationList
        """
        return UserService.get_user_notifications(), 200
    

@user.route('/device/token', methods=['POST'])
class DeviceToken(Resource):
    @login_required
    @user.expect(deviceTokenModel)
    def post(self):
        """
        DeviceToken
        """
        content = request.json
        return UserService.update_device_token(content['device_token']), 200
    

@user.route('/info', methods=['GET'])
class GetUserInfo(Resource):
    @login_required
    def get(self):
        """
        GetUserInfo
        """
        return UserService.get_user_info(), 200