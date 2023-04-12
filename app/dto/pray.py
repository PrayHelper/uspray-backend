from dataclasses import dataclass
from typing import Union
from uuid import UUID
import uuid
from app.models import db
from app.models.pray import Pray


@dataclass
class PrayDTO:
    id: Union[int, None]
    user_id: UUID
    target: str
    title: str

    def to_model(self) -> Pray:
        return Pray(
            id=self.id,
            user_id=self.user_id,
            target=self.target,
						title=self.title
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
    def create_pray(user_id: str, target: str, title: str) -> 'PrayDTO':
        """
        새로운 기도를 생성합니다.
        """
        if not user_id:
            raise ValueError("작성자는 필수 입력 항목입니다.")
        if not target:
            raise ValueError("기도 대상자는 필수 입력 항목입니다.")
        if not title:
            raise ValueError("기도 제목은 필수 입력 항목입니다.")
        
				#user_id가 user테이블에 존재하는지 확인해야하나?
        pray_dto = PrayDTO(
            id=None,
            user_id=user_id,
            target=target,
						title=title
        )
        pray_dto.save()
        return pray_dto
