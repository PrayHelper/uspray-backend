from dataclasses import dataclass
from typing import Union
from uuid import UUID
from app.error_handler import SignUpFail
import datetime
import uuid
from app.models import db
from app.models.pray import Pray

@dataclass
class PrayDTO:
    id: Union[UUID, None]
    userId: str
    target: str
    title: str
    content: str
    created_at: datetime

    def to_model(self) -> Pray:
        return Pray(
            id=self.id,
            userId=self.userId,
            target=self.target,
            title=self.title,
            content=self.content,
            created_at=datetime.datetime.now()
        )
    
    def save(self):
        try:
            pray = self.to_model()
            db.session.add(pray)
            db.session.commit()
            self = pray
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
    def create_pray(userId: str, target: str, title: str, content: str) -> 'PrayDTO':
        """
        새로운 유저를 생성합니다.
        """
        if not userId:
            raise SignUpFail('userId is required')
        if not target:
            raise SignUpFail('target is required')
        if not title:
            raise SignUpFail('title is required')
        if not content:
            raise SignUpFail('content is required')
        return PrayDTO(
            id=uuid.uuid4(),
            userId=userId,
            target=target,
            title=title,
            content=content,
            created_at=datetime.datetime.now()
        )