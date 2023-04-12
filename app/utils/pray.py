from dataclasses import dataclass
from typing import Union
from uuid import UUID
from app.utils.error_handler import PrayFail, StorageFail
import datetime
import uuid
from app.models import db
from app.models.pray import Pray, Storage

@dataclass
class PrayDTO:
    id: Union[int, None]
    user_id: UUID
    target: str
    title: str

    def __init__(self, user_id, target, title):
        self.user_id = user_id
        self.target = target
        self.title = title
        if not user_id:
            raise PrayFail('user_id is required')
        if not target:
            raise PrayFail('target is required')
        if not title:
            raise PrayFail('title is required')

@dataclass
class PrayDAO:
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
    def create_pray(pray_dto) -> 'PrayDAO':
        """
        새로운 기도제목을 생성합니다.
        """
        pray_dao = PrayDAO(
            id=None,
            user_id=pray_dto.user_id,
            target=pray_dto.target,
            title=pray_dto.title,
        )
        pray_dao.save()
        return pray_dao

@dataclass
class StorageDTO:
    id: Union[int, None]
    pray_id: int
    user_id: UUID
    pray_cnt: int
    deadline: datetime

    def __init__(self, pray_id, user_id, pray_cnt, deadline, created_at):
        self.user_id = user_id
        self.pray_id = pray_id
        self.pray_cnt = pray_cnt
        self.deadline = deadline
        self.created_at = created_at
        if not user_id:
            raise StorageFail('user_id is required')
        if not pray_id:
            raise StorageFail('pray_id is required')
        if not pray_cnt:
            raise StorageFail('pray_cnt is required')
        if not deadline:
            raise StorageFail('deadline is required')

@dataclass
class StorageDAO:
    id: Union[int, None]
    pray_id: int
    user_id: UUID
    pray_cnt: int
    deadline: datetime

    def to_model(self) -> Storage:
        return Storage(
            id=self.id,
            pray_id=self.pray_id,
            user_id=self.user_id,
            pray_cnt=self.pray_cnt,
            deadline=self.deadline,
            created_at=datetime.datetime.now()
        )
    
    def save(self):
        try:
            storage = self.to_model()
            db.session.add(storage)
            db.session.commit()
            self = storage
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
    def create_storage(storage_dto) -> 'StorageDAO':
        """
        새로운 보관함을 생성합니다.
        """
        storage_dao = StorageDAO(
            id=None,
            pray_id=storage_dto.pray_id,
            user_id=storage_dto.user_id,
            pray_cnt=storage_dto.pray_cnt,
            deadline=storage_dto.deadline,
        )
        storage_dao.save()
        return storage_dao