from dataclasses import dataclass
from typing import Union
from uuid import UUID
from app.utils.error_handler import SignUpFail
import datetime
from app.models import db
from app.models.user import User
import bcrypt
import re
from flask import g

@dataclass
class UserDTO:
    id: Union[UUID, None]
    uid: str
    password: str
    name: str
    gender: str
    birth: datetime
    phone: str

    def __init__(self, uid, password, name, gender, birth, phone, id=None):
        self.uid = uid
        self.password = password
        self.name = name
        self.gender = gender
        self.birth = birth
        self.phone = phone
        self.id = id

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
            self.id = user.id

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
    

    def get_user_by_id(self, user_id):
        return User.query.filter_by(id=user_id).first()
    
    def get_user_by_id(self, user_id):
        return User.query.filter_by(id=user_id).first()
    

class UserService:
    def update_password(user_id, password):
        user = User.query.filter_by(uid=user_id).first()
        if user is None:
            raise Exception("존재하지 않는 유저입니다.")
        
        pw_pattern = r'^[a-zA-Z0-9!@#$%^&*()_+{}|:"<>?~\[\]\\;\',./]{8,16}$'
        pw_reg = bool(re.match(pw_pattern,password))
        if not pw_reg:
            raise SignUpFail("비밀번호 형식이 잘못되었습니다. (8~16 영문대소, 숫, 특수)")
        
        new_password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
        user.password = new_password.decode('UTF-8')
        db.session.commit()
        return str(new_password)


    def create_user(user) -> 'UserDTO':
        """
        새로운 유저를 생성합니다.
        """
        uid_pattern = r'^[a-z0-9]{6,15}$'
        pw_pattern = r'^[a-zA-Z0-9!@#$%^&*()_+{}|:"<>?~\[\]\\;\',./]{8,16}$'
        phone_pattern = r'^01([0|1|6|7|8|9])?([0-9]{3,4})?([0-9]{4})$'
        uid_reg = bool(re.match(uid_pattern, user.uid))
        pw_reg = bool(re.match(pw_pattern, user.password))
        phone_reg = bool(re.match(phone_pattern, user.phone))
        if not uid_reg:
            raise SignUpFail("아이디 형식이 잘못되었습니다. (6~15 영문소, 숫)")
        if not pw_reg:
            raise SignUpFail("비밀번호 형식이 잘못되었습니다. (8~16 영문대소, 숫, 특수)")
        if not phone_reg:
            raise SignUpFail("전화번호 형식이 잘못되었습니다. (01012345678 형식))")

        dup_user_id = User.query.filter_by(uid=user.uid).first()
        dup_phone = User.query.filter_by(phone=user.phone).first()
        
        if dup_user_id is not None:
            raise SignUpFail("중복된 아이디가 존재합니다.")
        if dup_phone is not None:
            raise SignUpFail("중복된 전화번호가 존재합니다.")
   
        new_password = bcrypt.hashpw(user.password.encode('UTF-8'), bcrypt.gensalt())

        user_dto = UserDTO(
            id=None,
            uid=user.uid,
            password=new_password.decode('UTF-8'),
            name=user.name,
            gender=user.gender,
            birth=user.birth,
            phone=user.phone
        )
        user_dto.save()
        return user_dto

    def update_phone(phone) -> UserDTO:
        """
        유저의 전화번호를 수정합니다.
        """
        phone_pattern = r'^01([0|1|6|7|8|9])?([0-9]{3,4})?([0-9]{4})$'
        phone_reg = bool(re.match(phone_pattern, phone))
        if not phone_reg:
            raise SignUpFail("전화번호 형식이 잘못되었습니다. (01012345678 형식))")

        user = User.query.filter_by(phone=phone).first()
        if user is not None:
            raise SignUpFail("중복된 전화번호가 존재합니다.")
        user = User.query.filter_by(id=g.user_id).first()
        user.phone = phone
        db.session.commit()
        return user
