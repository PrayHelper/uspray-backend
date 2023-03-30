import base64
import hashlib
import hmac
import time
import requests
import json
import random
import os
from functools import wraps
from urllib import request
import jwt
from flask import g, request

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get("Authorization")  #??

        if access_token is not None: 
            try:
                payload = jwt.decode(access_token, os.getenv('SECRET_KEY'), algorithm="HS256")
            except jwt.InvalidTokenError:
                return { "message": "INVALID TOKEN" }, 401
            return f(*args, **kwargs)
        else:
            return { "message": "INVALID TOKEN" }, 401
    return decorated_function