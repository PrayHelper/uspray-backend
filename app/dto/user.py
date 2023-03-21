from dataclasses import dataclass
from typing import Union
from uuid import UUID
import datetime
import uuid
from app import db
from app.models.user import User

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
            phone=self.phone
        )
    
    def save(self):
        try:
            db.session.begin()
            user = self.to_model()
            db.session.add(user)
            db.session.commit()
            self.id = user.id
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        try:
            db.session.begin()
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            print(222222)
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
      
        user_dto = UserDTO(
            id=None,
            uid=uid,
            password=password,
            name=name,
            gender=gender,
            birth=birth,
            phone=phone
        )
        user_dto.save()
        return user_dto