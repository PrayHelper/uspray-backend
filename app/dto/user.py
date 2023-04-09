from dataclasses import dataclass
from typing import Union
from uuid import UUID
from app.error_handler import SignUpFail
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
            raise SignUpFail("아이디는 필수 입력 항목입니다.")
        if not password:
            raise SignUpFail("비밀번호는 필수 입력 항목입니다.")
        if not name:
            raise SignUpFail("이름은 필수 입력 항목입니다.")
        if not gender:
            raise SignUpFail("성별은 필수 입력 항목입니다.")
        if not birth:
            raise SignUpFail("생일은 필수 입력 항목입니다.")
        if not phone:
            raise SignUpFail("전화번호는 필수 입력 항목입니다.")

       
        uidPattern = '^[a-z0-9]{6,15}$'
        pwPattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,16}$'
        phonePattern = r'^01([0|1|6|7|8|9])?([0-9]{3,4})?([0-9]{4})$'
        uidReg = bool(re.match(uidPattern, uid))
        pwReg = bool(re.match(pwPattern, password))
        phoneReg = bool(re.match(phonePattern, phone))
        if not uidReg:
            raise SignUpFail("아이디 형식이 잘못되었습니다. (6~15 영문소, 숫)")
        if not pwReg:
            raise SignUpFail("비밀번호 형식이 잘못되었습니다. (8~16 영문대소, 숫, 특수)")
        if not phoneReg:
            raise SignUpFail("전화번호 형식이 잘못되었습니다. (01012345678 형식))")

        dupUserId = User.query.filter_by(uid=uid).first()
        dupPhone = User.query.filter_by(phone=phone).first()
        if dupUserId is not None:
            raise SignUpFail("중복된 아이디가 존재합니다.")
        if dupPhone is not None:
            raise SignUpFail("중복된 전화번호가 존재합니다.")
        
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
