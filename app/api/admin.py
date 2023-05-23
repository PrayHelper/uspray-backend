from flask import Blueprint, request
from flask_restx import Namespace, Resource
from app.utils.user import UserService
from .utils import send
import datetime


admin = Namespace('admin', description='admin stest API')
sms_string = admin.parser()
sms_string.add_argument('phone', required=True, help='01012345678')

@admin.route('')
class Main(Resource):
    def get(self):
        return {'message': 'Hello World'}
    

@admin.route('/sms')
class SmsSend(Resource):
    @admin.expect(sms_string)
    def post(self):
        """
        Send SMS and verify code
        """
        verify_code = None
        phone = sms_string.parse_args().get('phone')
        if phone:
            try:
                verify_code = send(phone)
            except Exception as e:
                print(e)
                return {'message': 'SMS 전송에 실패하였습니다.'}, 400
        return { 'code': verify_code, 'send_time': datetime.datetime.now().strftime('%Y-%m-%d') }


@admin.route('/notifications')
class Notification(Resource):
    def get(self):
        """
        Get notifications
        """
        return UserService.get_notifications(), 200