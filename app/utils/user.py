from dataclasses import dataclass
from typing import Union
from uuid import UUID
from app.utils.error_handler import SignUpFail, UserFail
import datetime
from app.models import db
from app.models.user import User, Notification, UserNotification, UserDelete, UserDeleteReason
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

    def __init__(self, uid, password, name, phone,  gender=None, birth=None, id=None):
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
        if not phone:
            raise SignUpFail("전화번호는 필수 입력 항목입니다.")
        
    def __repr__(self):
        return {
            'uid': self.uid,
            'name': self.name,
            'gender': self.gender,
            'birth': self.birth.strftime("%Y-%m-%d %H:%M:%S"),
            'phone': self.phone
        }

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
    def reset_password(user):
        reset_pw = bcrypt.hashpw(str(user.id).encode('UTF-8'), bcrypt.gensalt())
        user.reset_pw = reset_pw.decode('UTF-8')
        db.session.commit()
        return reset_pw.decode('UTF-8')

    
    def find_password(user, password):
        pw_pattern = r'^[a-zA-Z0-9!@#$%^&*()_+{}|:"<>?~\[\]\\;\',./]{8,16}$'
        pw_reg = bool(re.match(pw_pattern,password))
        if not pw_reg:
            raise UserFail("비밀번호 형식이 잘못되었습니다. (8~16 영문대소, 숫, 특수)")
        
        new_password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
        user.password = new_password.decode('UTF-8')
        db.session.commit()


    def update_password(password):
        user = User.query.filter_by(id=g.user_id).first()
        if user is None:
            raise UserFail("존재하지 않는 유저입니다.")
        
        pw_pattern = r'^[a-zA-Z0-9!@#$%^&*()_+{}|:"<>?~\[\]\\;\',./]{8,16}$'
        pw_reg = bool(re.match(pw_pattern,password))
        if not pw_reg:
            raise UserFail("비밀번호 형식이 잘못되었습니다. (8~16 영문대소, 숫, 특수)")
        
        new_password = bcrypt.hashpw(password.encode('UTF-8'), bcrypt.gensalt())
        user.password = new_password.decode('UTF-8')
        db.session.commit()


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
            return { "message": "아이디 형식이 잘못되었습니다. (6~15 영문소, 숫)" }, 400
        if not pw_reg:
            return { "message": "비밀번호 형식이 잘못되었습니다. (8~16 영문대소, 숫, 특수)" }, 400
        if not phone_reg:
            return { "전화번호 형식이 잘못되었습니다. (01012345678 형식))" }, 400

        dup_user_id = User.query.filter_by(uid=user.uid).first()
        dup_phone = User.query.filter_by(phone=user.phone).filter_by(deleted_at=None).first()
        
        if dup_user_id is not None:
            return {"message": "중복된 아이디가 존재합니다." }, 400
        if dup_phone is not None:
            return {"message": "중복된 전화번호가 존재합니다."}, 400
   
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

        notifications = Notification.query.all()
        for notification in notifications:
            user_notification = UserNotification(
                user_id=user_dto.id,
                notification_id=notification.id,
                is_enabled=True
            )
            db.session.add(user_notification)
        db.session.commit()
        return {"message": "회원가입이 완료되었습니다."}, 200

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

    def delete_user(withdrawalModel):
        """
        유저를 삭제합니다.
        """
        user = User.query.filter_by(id=g.user_id).first()
        if user is None:
            raise UserFail("존재하지 않는 유저입니다.")
        for id in withdrawalModel["reason_id"]:
            delete_reason = UserDeleteReason.query.filter_by(id=id).first()
            if delete_reason is None:
                raise UserFail("존재하지 않는 탈퇴 사유입니다.")
            if id == 5:
                if not withdrawalModel["etc"]:
                    raise UserFail("기타 사유를 입력해주세요.")
                user_delete = UserDelete(
                    user_id=g.user_id,
                    reason_id=delete_reason.id,
                    etc=withdrawalModel["etc"]
                )
            else:
                user_delete = UserDelete(
                    user_id=g.user_id,
                    reason_id=delete_reason.id
                )
            db.session.add(user_delete)
        user.deleted_at = datetime.datetime.now()
        db.session.commit()
        return user
    
    def enable_notification(notification_id):
        """
        유저의 알림을 활성화합니다.
        """
        user_notification = UserNotification.query.filter(UserNotification.user_id == g.user_id, UserNotification.notification_id == notification_id).first()
        try: 
            if user_notification is None:
                new_user_notification = UserNotification(
                    user_id=g.user_id,
                    notification_id=notification_id
                )
                db.session.add(new_user_notification)
                db.session.commit()
            else:
                user_notification.is_enabled = True
                db.session.commit()
        except:
            db.session.rollback()
            raise UserFail("알림에서 에러가 발생했습니다.")

    def disable_notification(notification_id):
        """
        유저의 알림을 비활성화합니다.
        """
        user_notification = UserNotification.query.filter(UserNotification.user_id == g.user_id, UserNotification.notification_id == notification_id).first()
        try:
            if user_notification is None:
                new_user_notification = UserNotification(
                    user_id=g.user_id,
                    notification_id=notification_id,
                    is_enabled=False
                )
                db.session.add(new_user_notification)
                db.session.commit()
            else:
                user_notification.is_enabled = False
                db.session.commit()
        except:
            db.session.rollback()
            raise UserFail("알림에서 에러가 발생했습니다.")
        
    
    def get_user_notifications():
        """
        유저의 알림을 가져옵니다.
        """
        user_notifications = UserNotification.query.filter(UserNotification.user_id == g.user_id).all()
        return [
            {
                "id": user_notification.notification.id,
                "content": user_notification.notification.content,
                "is_enabled": user_notification.is_enabled
            }
            for user_notification in user_notifications
        ]
    

    def get_notifications():
        """
        알림 목록을 가져옵니다.
        """
        notifications = Notification.query.all()
        return [
            {
                "id": notification.id,
                "content": notification.content
            }
            for notification in notifications
        ]

    def update_device_token(device_token):
        """
        유저의 디바이스 토큰을 저장합니다.
        """
        try:
            user = User.query.filter_by(id=g.user_id).first()
            user.device_token = device_token
            db.session.commit()
            return { "message": "디바이스 토큰이 저장되었습니다." }
        except:
            db.session.rollback()
            raise UserFail("디바이스 토큰 저장에 실패했습니다.")
        

    def get_user_info():
        try:
            user = User.query.filter_by(id=g.user_id).first()
            return UserDTO(
                id=user.id,
                uid=user.uid,
                password=user.password,
                phone=user.phone,
                gender=user.gender,
                birth=user.birth,
                name=user.name,
            ).__repr__()
        except Exception as e:
            raise UserFail("유저 정보를 가져오는데 실패했습니다.")
