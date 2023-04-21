import os
from functools import wraps
from urllib import request
import jwt
from flask import g, request

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get("Authorization")

        if access_token is not None: 
            try:
                payload = jwt.decode(access_token, os.getenv('SECRET_KEY'), algorithm="HS256")
            except jwt.InvalidTokenError:
                return { "message": "INVALID TOKEN" }, 401
            return f(*args, **kwargs)
        else:
            return { "message": "INVALID TOKEN" }, 401
    return decorated_function