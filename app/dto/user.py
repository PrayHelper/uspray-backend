from dataclasses import dataclass
from typing import Union
from uuid import UUID
import datetime
import uuid
from app.models import db
from app.models.user import User
import bcrypt
import re


@dataclass
class UserDTO:
    id: Union[UUID, None]
    uid: str
    password: str
    name: str
    gender: str
    birth: datetime
    phone: str

    def to_model(self) -> User:
        return User(
            id=self.id,
            uid=self.uid,
            password=self.password,
            name=self.name,
            gender=self.gender,
            birth=self.birth,
            phone=self.phone,
            created_at=datetime.datetime.now()
        )
    
    def save(self):
        try:
            user = self.to_model()
            db.session.add(user)
            db.session.commit()
            self = user
        except Exception as e:
            db.session.rollback()
            db.session.close()
            raise e

    def delete(self):
        try:
            db.session.begin()
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def create_user(uid: str, password: str, name: str, gender: str, birth: datetime, phone: str) -> 'UserDTO':
        """
        새로운 유저를 생성합니다.
        """
        if not uid:
            raise ValueError("uid must not be empty")
        if not password:
            raise ValueError("password must not be empty")

        dupUserId = User.query.filter_by(uid=uid).first()
        dupPhone = User.query.filter_by(phone=phone).first()
        if dupUserId is not None:
            raise ValueError("duplicate uid")
        if dupPhone is not None:
            raise ValueError("duplicate phone num")
       
        uidPattern = '^[a-z0-9]{6,15}$'
        pwPattern = '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{8,}'
        uidReg = bool(re.match(uidPattern, uid))
        pwReg = bool(re.match(pwPattern, password))
        if not uidReg:
            raise ValueError("Id must be alphanumeric with no spaces")
        if not pwReg:
            raise ValueError("Password must be at least 8 characters long, contain at least one uppercase letter, one lowercase letter, and one number")

        new_password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())

        user_dto = UserDTO(
            id=None,
            uid=uid,
            password=new_password.decode('UTF-8'),
            name=name,
            gender=gender,
            birth=birth,
            phone=phone
        )
        user_dto.save()
        return user_dto
