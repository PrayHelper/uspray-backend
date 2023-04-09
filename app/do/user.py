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

    def __init__(self, uid, password, name, gender, birth, phone):
        self.uid = uid
        self.password = password
        self.name = name
        self.gender = gender
        self.birth = birth
        self.phone = phone
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

class UserDAO:
    id: Union[UUID, None]
    uid: str
    password: str
    name: str
    gender: str
    birth: datetime
    phone: str

    def __init__(self, id, uid, password, name, gender, birth, phone):
        self.id = id
        self.uid = uid
        self.password = password
        self.name = name
        self.gender = gender
        self.birth = birth
        self.phone = phone 
            

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
    def create_user(user_dto) -> 'UserDAO':
        """
        새로운 유저를 생성합니다.
        """
        uid_pattern = r'^[a-z0-9]{6,15}$'
        pw_pattern = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[$@$!%*#?&])[A-Za-z\d$@$!%*#?&]{8,16}$'
        phone_pattern = r'^01([0|1|6|7|8|9])?([0-9]{3,4})?([0-9]{4})$'
        uid_reg = bool(re.match(uid_pattern, user_dto.uid))
        pw_reg = bool(re.match(pw_pattern, user_dto.password))
        phone_reg = bool(re.match(phone_pattern, user_dto.phone))
        if not uid_reg:
            raise SignUpFail("아이디 형식이 잘못되었습니다. (6~15 영문소, 숫)")
        if not pw_reg:
            raise SignUpFail("비밀번호 형식이 잘못되었습니다. (8~16 영문대소, 숫, 특수)")
        if not phone_reg:
            raise SignUpFail("전화번호 형식이 잘못되었습니다. (01012345678 형식))")

        dup_user_id = User.query.filter_by(uid=user_dto.uid).first()
        dup_phone = User.query.filter_by(phone=user_dto.phone).first()
        if dup_user_id is not None:
            raise SignUpFail("중복된 아이디가 존재합니다.")
        if dup_phone is not None:
            raise SignUpFail("중복된 전화번호가 존재합니다.")
        
        new_password = bcrypt.hashpw(user_dto.password.encode('UTF-8'), bcrypt.gensalt())

        user_dao = UserDAO(
            id=None,
            uid=user_dto.uid,
            password=new_password.decode('UTF-8'),
            name=user_dto.name,
            gender=user_dto.gender,
            birth=user_dto.birth,
            phone=user_dto.phone
        )
        user_dao.save()
        return user_dao
    

    def get_user_by_id(self, user_id):
        return User.query.filter_by(id=user_id).first()