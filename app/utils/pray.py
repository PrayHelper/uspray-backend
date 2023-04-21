from dataclasses import dataclass
from uuid import UUID
from app.utils.error_handler import PrayFail, StorageFail
import datetime
from app.models import db
from typing import List, Optional, Union
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
            self.id = pray.id
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

        if pray_dto.title == "":
            raise PrayFail("기도제목이 비었습니다.")
        if pray_dto.target == "":
            raise PrayFail("기도대상이 비었습니다.")

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
    pray_id: int
    user_id: UUID
    deadline: datetime
    id: Union[id, None]
    pray_cnt: Optional[int] = None
    created_at: Union[dataclass, None] = None
    pray: PrayDAO = None

    def __init__(self, pray_id, user_id, deadline, pray_cnt=None, id=None, created_at=None, pray=None):
        self.pray_id = pray_id
        self.user_id = user_id
        self.deadline = deadline
        self.pray_cnt = pray_cnt
        self.id = id
        self.created_at = created_at
        self.pray = pray
        
        if not user_id:
            raise StorageFail('user_id is required')
        if not pray_id:
            raise StorageFail('pray_id is required')
        if not deadline:
            raise StorageFail('deadline is required')


    def __repr__(self):
        return {
            'id': self.id,
            'pray_id': self.pray_id,
            'target': self.pray.target,
            'title': self.pray.title,
            'pray_user_id': str(self.pray.user_id),
            'user_id': str(self.user_id),
            'pray_cnt': self.pray_cnt,
            'deadline': self.deadline.strftime("%Y-%m-%d"),
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
            
       
    
@dataclass
class StorageDAO:
    id: Union[int, None]
    pray_id: int
    user_id: UUID
    pray_cnt: Union[int, None]
    deadline: datetime
    created_at: Union[dataclass, None]
    pray: Union[PrayDAO, None]

    def __init__(self, id, pray_id, user_id, deadline, pray_cnt=0, created_at=None, pray=None):
        self.id = id
        self.pray_id = pray_id
        self.user_id = user_id
        self.pray_cnt = pray_cnt
        self.deadline = deadline
        self.created_at = created_at
        self.pray = pray

    def __repr__(self):
        return {
            'id': self.id,
            'pray_id': self.pray_id,
            'target': self.pray.target,
            'title': self.pray.title,
            'pray_user_id': str(self.pray.user_id),
            'user_id': str(self.user_id),
            'pray_cnt': self.pray_cnt,
            'deadline': self.deadline,
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

    def to_model(self) -> Storage:
        return Storage(
            id=self.id,
            pray_id=self.pray_id,
            user_id=self.user_id,
            deadline=self.deadline
        )
    
    def to_dao(storage) -> 'StorageDAO':
        return StorageDAO(
            id=storage.id,
            pray_id=storage.pray_id,
            user_id=storage.user_id,
            deadline=storage.deadline,
            pray_cnt=storage.pray_cnt,
            created_at=storage.created_at,
            pray=storage.pray
        ).__repr__()
    
    def save(self):
        try:
            storage = self.to_model()
            db.session.add(storage)
            db.session.commit()
            self.id = storage.id
            self.pray = storage.pray
            self.created_at = storage.created_at
        except Exception as e:
            pray = Pray.query.filter_by(pray_id=self.pray_id).first()
            db.session.rollback()
            db.session.delete(pray)
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
            deadline=storage_dto.deadline,
        )
        storage_dao.save()
        return storage_dao.__repr__()

    @staticmethod
    def delete_storage(storage_dto):
        """
        보관함을 삭제합니다.
        """
        storage_dao = StorageDAO(
            id=None,
            pray_id=storage_dto.pray_id,
            user_id=storage_dto.user_id,
            deadline=storage_dto.deadline,
        )
        storage_dao.delete()


class StorageService:
    def get_storages(user_id) -> List[StorageDTO]:
        storages = Storage.query.filter_by(user_id=user_id).all()
        storage_dtos = [
            StorageDTO(
                id=storage.id,
                pray_id=storage.pray_id,
                user_id=storage.user_id,
                pray_cnt=storage.pray_cnt,
                deadline=storage.deadline,
                created_at=storage.created_at,
                pray=storage.pray
            ).__repr__()
            for storage in storages
        ]
        return (storage_dtos)
    
    def get_storage(storage_id) -> StorageDTO:
        storage = Storage.query.filter_by(id=storage_id).first()
        if not storage:
            raise StorageFail('storage not found')
        try:
            return StorageDTO(
                id=storage.id,
                pray_id=storage.pray_id,
                user_id=storage.user_id,
                pray_cnt=storage.pray_cnt,
                deadline=storage.deadline,
                created_at=storage.created_at,
                pray=storage.pray
            ).__repr__()
        except Exception:
            raise StorageFail('get storage error')

    def delete_storage(storage_id):
        storage = Storage.query.filter_by(id=storage_id).first()
        if not storage:
            raise StorageFail('storage not found')
        try:
            storage_dto = StorageDTO(
                id=storage.id,
                pray_id=storage.pray_id,
                user_id=storage.user_id,
                pray_cnt=storage.pray_cnt,
                deadline=storage.deadline,
                created_at=storage.created_at,
                pray=storage.pray
            )
            StorageDAO.delete_storage(storage_dto)
        except Exception:
            raise StorageFail('delete storage error')
