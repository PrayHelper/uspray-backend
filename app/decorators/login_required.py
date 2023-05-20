import os
from functools import wraps
import jwt
import datetime
from flask import g, request
from app.models.user import User
from app.utils.error_handler import InvalidTokenError


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get("Authorization")
        
        if access_token:
            try:
                payload = jwt.decode(access_token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
                user_id = payload['id']
                if 'access_token_exp' in payload:
                    access_token_exp = payload['access_token_exp']
                    if datetime.datetime.fromisoformat(access_token_exp) < datetime.datetime.now():
                        raise InvalidTokenError("access token expired", 403, 403)
                    u = User.query.filter_by(id=user_id).first()
                    if u is not None and u.deleted_at is None:
                        g.user_id = user_id
                        g.user = u
                    else:
                        g.user = None
                        raise InvalidTokenError("user not found")
            except jwt.InvalidTokenError:
                raise InvalidTokenError("invalid token")
            return f(*args, **kwargs)
        else:
            raise InvalidTokenError("token not found")
    return decorated_function