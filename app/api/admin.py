from flask import Blueprint, request
from flask_restx import Namespace, Resource, fields
from app.utils.user import UserService
from app.api.utils import send_push_notification
from .utils import send
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import json

admin = Namespace('admin', description='admin stest API')
sms_string = admin.parser()
sms_string.add_argument('phone', required=True, help='01012345678')

send_push_model = admin.model('SendPush', {
    'token': fields.List(fields.String, required=True, description='token'),
    'title': fields.String(required=False, description='title'),
    'body': fields.String(required=False, description='body'),
    'data': fields.Raw(required=False, description='data')
})

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
    

@admin.route('/send/push', methods=['POST'])
class Push(Resource):
    @admin.doc(response={ 200: 'Push Send' })
    @admin.doc(response={ 400: 'Invalid Request' })
    @admin.expect(send_push_model)
    def post(self):
        """
        Send Push
        """
        content = request.json
        response = send_push_notification(content['title'], content['body'], content['token'], content['data'])
        return { 'res' : '{0} messages were sent successfully'.format(response.success_count) }, 200