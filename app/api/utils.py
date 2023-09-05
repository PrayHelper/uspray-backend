import base64
import hashlib
import hmac
import time
import requests
import json
import random
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import json

def send(phone):
    try:
      accessKey = os.getenv('accessKey')
      service_id = os.getenv('service_id')
      from_phone = os.getenv('from_phone')
      url = "https://sens.apigw.ntruss.com"
      uri = "/sms/v2/services/" + service_id + "/messages"
      api_url = url + uri
      timestamp = str(int(time.time() * 1000))
      access_key = accessKey
      string_to_sign = "POST " + uri + "\n" + timestamp + "\n" + access_key
      signature = make_signature(string_to_sign)
      verify_code = random.randint(100000, 999999)
    except Exception as e:
      print(e)
      return { 'res' : 'error occured at send' }, 400

    headers = {
        'Content-Type': "application/json; charset=UTF-8",
        'x-ncp-apigw-timestamp': timestamp,
        'x-ncp-iam-access-key': access_key,
        'x-ncp-apigw-signature-v2': signature
    }
    body = {
        "type": "SMS",
        "from": from_phone,
        "content": verify_code,
        "messages": [
            {
                "subject": verify_code,
                "content": f"인증번호입니다. [{verify_code}]",
                "to": phone
            }
        ]
    }

    body = json.dumps(body)
    response = requests.post(api_url, headers=headers, data=body)
    response.raise_for_status()
    return verify_code


def make_signature(string):
    secretKey = os.getenv('secretKey')
    secret_key = bytes(secretKey, 'UTF-8')
    string = bytes(string, 'UTF-8')
    string_hmac = hmac.new(secret_key, string, digestmod=hashlib.sha256).digest()
    string_base64 = base64.b64encode(string_hmac).decode('UTF-8')
    return string_base64


def send_push_notification(title, body, token, data):
    if not firebase_admin._apps:
        cred = credentials.Certificate('app/service-account-file.json')
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.get_app()
    registration_token = token
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data=data,
        tokens=registration_token,
    )
    response = messaging.send_multicast(message)
    print('Successfully sent message:', response)
    print('Failure send message:', response.failure_count)
    return response