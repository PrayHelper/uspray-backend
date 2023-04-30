import os
from functools import wraps
import jwt
from flask import g, request
from app.models.user import User


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get("Authorization")
        
        if access_token is not None: 
            try:
                payload = jwt.decode(access_token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
                user_id = payload['id']
                u = User.query.filter_by(id=user_id).first()
                if u is not None:
                    g.user_id = user_id
                    g.user = u
                else:
                    g.user = None
                    return { "message": "INVALID_USER" }, 401
            except jwt.InvalidTokenError:
                return { "message": "INVALID TOKEN" }, 401
            return f(*args, **kwargs)
        else:
            return { "message": "INVALID TOKEN" }, 401
    return decorated_function