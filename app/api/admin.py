from flask import Blueprint, request
from flask_restx import Namespace, Resource
from .utils import send


admin = Namespace('admin', description='admin stest API')
sms_string = admin.parser()
sms_string.add_argument('phone', required=True, help='phone')

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
        return verify_code