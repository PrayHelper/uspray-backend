from flask_restx import Namespace, Resource, fields
from flask import request, g
import bcrypt
import datetime
import jwt
import os
import requests

from app.models.user import UserLocalAuth, UserSocialAuth, User, UserProfile
from app.utils.user import UserProfileDTO, UserService
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

SocialUserModel = user.model('SocialUser', {
    'name': fields.String(required=True, default='name', description='user name'),
    'gender': fields.String(required=True, default='여', description='user gender'),
    'birth': fields.Date(required=True, default='2023-03-20', description='user birth'),
    'phone': fields.String(required=True, default='01012345678', description='user phone'),
    'user_id': fields.String(required=True, default='UUID', description='user id'),
})

@user.route('/signup', methods=['POST'])
class SignUp(Resource):
    @user.expect(userModel)
    def post(self):
        """
        Signup
        """
        content = request.json
        user = UserService.create_user()
        user_profile_dto = UserProfileDTO(
            user_id=user.id,
            name=content['name'],
            gender=content['gender'],
            birth=content['birth'],
            phone=content['phone']
        )
        UserService.create_local_user(user, user_profile_dto, content['id'], content['password'])
        return { 'message': '회원가입 되었습니다' }, 200


@user.route('/dup_check/<string:id>', methods=['GET'])
class IdDupCheck(Resource):
    @user.doc(params={'id': 'uos920'})
    def get(self, id):
        """
        IdDupCheck
        """
        dupUserId = UserLocalAuth.query.filter_by(id=id).first()
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

        u = UserLocalAuth.query.filter_by(id=content['id']).first()
        if u is None:
            return { 'message' : '아이디가 존재하지 않습니다.' }, 400
        if u.user.deleted_at is not None:
            return { 'message' : '탈퇴한 회원입니다.' }, 400
        if bcrypt.checkpw(content['password'].encode('UTF-8'), u.password.encode('UTF-8')):
            access_payload = {
                'id': str(u.user_id),
                'access_token_exp': (datetime.datetime.now() + datetime.timedelta(minutes=60*24)).isoformat()
            }
            access_token = jwt.encode(access_payload, os.getenv('SECRET_KEY'), algorithm="HS256")

            refresh_payload = {
                'id': str(u.user_id),
                'refresh_token_exp': (datetime.datetime.now() + datetime.timedelta(minutes=60*24*60)).isoformat()
            }
            refresh_token = jwt.encode(refresh_payload, os.getenv('SECRET_KEY'), algorithm="HS256")
            return { 'access_token': access_token, 'refresh_token': refresh_token, 'user_id': u.id }, 200
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
        u = UserProfile.query.filter_by(name=content['name'], phone=content['phone']).first()

        if u is None:
            return { 'message' : '유저가 존재하지 않습니다.' }, 400
        user = UserLocalAuth.query.filter_by(user_id=u.user_id).first()
        return { 'message': user.id }, 200
    


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

        u = UserLocalAuth.query.filter_by(reset_pw=token).first()
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
        u = UserLocalAuth.query.join(UserProfile, UserLocalAuth.user_id == UserProfile.user_id).filter(UserLocalAuth.id == content['id'], UserProfile.phone == content['phone']).first()

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
        user = g.local_auth
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


@user.route('/oauth/kakao', methods=['GET'])
class KakaoOauth(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    def get(self):
        code = str(request.args.get('code'))

        oauth_token = requests.post(
            url="https://kauth.kakao.com/oauth/token",
            headers={
                "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
            },
            data={
                "grant_type": "authorization_code",
                "client_id": os.getenv('KAKAO_API_KEY'),
                "client_secret": os.getenv('KAKAO_CLIENT_SECRET'),
                "redirect_uri": os.getenv('KAKAO_URI'),
                "code": code,
            }, 
        ).json()

        kakao_access_token = oauth_token["access_token"]
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {kakao_access_token}"}
        ).json()

        u = UserSocialAuth.query.filter_by(id=str(profile_request['id'])).first()
        if u:
            #login
            access_payload = {
                'id': str(u.user_id),
                'access_token_exp': (datetime.datetime.now() + datetime.timedelta(minutes=60*24)).isoformat()
            }
            access_token = jwt.encode(access_payload, os.getenv('SECRET_KEY'), algorithm="HS256")

            refresh_payload = {
                'id': str(u.user_id),
                'refresh_token_exp': (datetime.datetime.now() + datetime.timedelta(minutes=60*24*60)).isoformat()
            }
            refresh_token = jwt.encode(refresh_payload, os.getenv('SECRET_KEY'), algorithm="HS256")
            return { 'access_token': access_token, 'refresh_token': refresh_token, 'user_id': u.id }, 200
        else:
            #signup
            user = UserService.create_user()
            content = {
                'id': profile_request['id'],
                'connected_at': profile_request['connected_at'],
                'social_type': 'kakao',
                'access_token': kakao_access_token
            }
            UserService.create_social_auth(user, content)
            return { 'message': '회원가입 되었습니다', 'user_id': str(user.id) }, 200


@user.route('/oauth/signup', methods=['POST'])
class OauthSignUp(Resource):
    @user.doc(responses={200: 'OK'})
    @user.doc(responses={400: 'Bad Request'})
    @user.expect(SocialUserModel)
    def post(self):
        content = request.json
        user_profile = UserProfileDTO(
            user_id=content['user_id'],
            name=content['name'],
            gender=content['gender'],
            birth=content['birth'],
            phone=content['phone']
        )
        user_profile.save()
        return { 'message': '회원가입 되었습니다' }, 200