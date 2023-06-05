from dataclasses import dataclass
from uuid import UUID
from app.utils.error_handler import PrayFail, StorageFail
import datetime
from flask import g
from app.models import db
from typing import List, Optional, Union
from app.models.pray import Pray, Storage, Complete, Share

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

    def __repr__(self):
        return {
            'id': self.id,
            'user_id': str(self.user_id),
            'target': self.target,
            'title': self.title
        }

    def to_model(self) -> Pray:
        return Pray(
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

@dataclass
class StorageDTO:
    pray_id: int
    user_id: UUID
    deadline: datetime
    id: Union[id, None]
    pray_cnt: Optional[int] = None
    created_at: Union[dataclass, None] = None
    pray: PrayDTO = None

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
            'target': self.pray.target,
            'title': self.pray.title,
            'user_id': str(self.user_id),
            'pray_cnt': self.pray_cnt,
            'deadline': self.deadline.strftime("%Y-%m-%d"),
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


    def history(self):
        origin_pray = Storage.query.filter_by(pray_id=self.pray_id).filter(Storage.deleted_at == None).order_by(Storage.created_at).first()
        return {
            'id': self.id,
            'target': self.pray.target,
            'title': self.pray.title,
            'pray_cnt': self.pray_cnt,
            'deadline': self.deadline.strftime("%Y-%m-%d"),
            'created_at': self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'origin_created_at': origin_pray.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'origin_user_name': self.pray.user.name
        }


    def to_model(self) -> Storage:
        return Storage(
            id=self.id,
            pray_id=self.pray_id,
            user_id=self.user_id,
            deadline=self.deadline
        )
    
    def save(self):
        try:
            storage = self.to_model()
            db.session.add(storage)
            db.session.commit()
            self.id = storage.id
            self.pray = storage.pray
            self.pray_cnt = storage.pray_cnt
            self.deadline = storage.deadline
            self.created_at = storage.created_at
        except Exception as e:
            pray = Pray.query.filter_by(pray_id=self.pray_id).first()
            db.session.rollback()
            db.session.delete(pray)
            db.session.close()
            raise e
        

class StorageService:
    def get_storages(args='date') -> List[StorageDTO]:
        current_time = datetime.datetime.now()
        today = current_time.date()
        midnight = datetime.datetime.combine(today, datetime.datetime.min.time())
        if args == 'date':
            storages_completed = Storage.query.join(Complete)\
                        .filter_by(user_id=g.user_id)\
                        .filter(Storage.deadline > midnight + datetime.timedelta(days=1))\
                        .filter(Complete.created_at >= midnight)\
                        .filter(Storage.deleted_at == None)\
                        .order_by(Storage.deadline).all()
            storages_uncompleted = Storage.query.outerjoin(Complete)\
                        .filter(Storage.user_id == g.user_id)\
                        .filter(Storage.deleted_at == None)\
                        .filter(Storage.deadline > midnight + datetime.timedelta(days=1))\
                        .filter((Complete.created_at < midnight) | (Complete.created_at == None))\
                        .order_by(Storage.deadline).all()
        elif args == 'cnt':
            storages_completed = Storage.query.join(Complete)\
                        .filter_by(user_id=g.user_id)\
                        .filter(Storage.deleted_at == None)\
                        .filter(Storage.deadline > midnight + datetime.timedelta(days=1))\
                        .filter(Complete.created_at >= midnight)\
                        .order_by(Storage.pray_cnt.desc()).all()
            storages_uncompleted = Storage.query.outerjoin(Complete)\
                        .filter(Storage.user_id == g.user_id)\
                        .filter(Storage.deleted_at == None)\
                        .filter(Storage.deadline > midnight + datetime.timedelta(days=1))\
                        .filter((Complete.created_at < midnight) | (Complete.created_at == None))\
                        .order_by(Storage.pray_cnt).all()
        storage_completed_dtos = [
            StorageDTO(
                id=storage.id,
                pray_id=storage.pray_id,
                user_id=storage.user_id,
                pray_cnt=storage.pray_cnt,
                deadline=storage.deadline,
                created_at=storage.created_at,
                pray=storage.pray
            ).__repr__()
            for storage in storages_completed
        ]
        storage_uncompleted_dtos = [
            StorageDTO(
                id=storage.id,
                pray_id=storage.pray_id,
                user_id=storage.user_id,
                pray_cnt=storage.pray_cnt,
                deadline=storage.deadline,
                created_at=storage.created_at,
                pray=storage.pray
            ).__repr__()
            for storage in storages_uncompleted
        ]

        return {
            'completed': storage_completed_dtos,
            'uncompleted': storage_uncompleted_dtos
        }
    

    def get_storage(storage_id) -> StorageDTO:
        storage = Storage.query.filter_by(id=storage_id, user_id=g.user_id).filter(Storage.deleted_at == None).first()
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
        

    def create_storage(pray_dto, deadline) -> StorageDTO:
        try:
            storage_dto = StorageDTO(
                pray_id=pray_dto.id,
                user_id=g.user_id,
                deadline=deadline
                # created_at=datetime.datetime.now()
            )
            storage_dto.save()
            return storage_dto.__repr__()
        except Exception:
            raise StorageFail('create storage error')
        

    def delete_storage(storage_id):
        storage = Storage.query.filter_by(id=storage_id, user_id=g.user_id).filter(Storage.deleted_at == None).first()
        if not storage:
            raise StorageFail('storage not found')

        share = Share.query.filter_by(pray_id=storage.pray_id).filter(Share.receipt_id != g.user_id).first()
        if share:
            raise StorageFail('share storage cannot be deleted')
        try:
            storage.deleted_at = datetime.datetime.now()
            db.session.commit()
        except Exception:
            raise StorageFail('delete storage error')
    

    def update_storage(storage_id, content) -> StorageDTO:
        storage = Storage.query.filter_by(id=storage_id, user_id=g.user_id).filter(Storage.deleted_at == None).first()
        if not storage:
            StorageFail('storage not found')
       
        try:
            if 'deadline' in content:
                storage.deadline = content['deadline']
            if 'pray_cnt' in content:
                storage.pray_cnt = content['pray_cnt']
            db.session.commit()
        except Exception:
            raise StorageFail('update storage error')
        return StorageDTO(
                id=storage.id,
                pray_id=storage.pray_id,
                user_id=storage.user_id,
                pray_cnt=storage.pray_cnt,
                deadline=storage.deadline,
                created_at=storage.created_at,
                pray=storage.pray
            ).__repr__()
    
    def finish_storage(storage_id):
        storage = Storage.query.filter_by(id=storage_id, user_id=g.user_id).filter(Storage.deleted_at == None).first()
        if not storage:
            raise StorageFail('storage not found')
        try:
            storage.deadline = datetime.datetime.now()
            db.session.commit()
        except Exception:
            raise StorageFail('finish storage error')

    def increase_cnt(storage_id):
        storage = Storage.query.filter_by(id=storage_id, user_id=g.user_id).filter(Storage.deleted_at == None).first()
        if not storage:
            raise StorageFail('storage not found')
        complete = Complete.query.filter_by(storage_id=storage.id, user_id=g.user_id).first()
        current_time = datetime.datetime.now()
        today = current_time.date()
        midnight = datetime.datetime.combine(today, datetime.datetime.min.time())
        try:    
            if complete:
                if complete.created_at >= midnight:
                    raise StorageFail('already increased today', 400)
                else:
                    complete.created_at = datetime.datetime.now()
            else:
                new_complete = Complete(storage_id=storage.id, user_id=g.user_id)
                db.session.add(new_complete)
            storage.pray_cnt += 1
            db.session.commit()
        except Exception as E:
            raise E


    def get_history(content):
        current_time = datetime.datetime.now()
        today = current_time.date()
        midnight = datetime.datetime.combine(today, datetime.datetime.min.time())
        if content['sort_by'] == 'cnt':
            storages = Storage.query.filter_by(user_id=g.user_id)\
                .filter(Storage.deadline < midnight)\
                .filter(Storage.deleted_at == None)\
                .order_by(Storage.pray_cnt.desc())\
                .paginate(page=content['page'], per_page=content['per_page'], error_out=False)
        else:
            storages = Storage.query.filter_by(user_id=g.user_id)\
                .filter(Storage.deadline < midnight)\
                .filter(Storage.deleted_at == None)\
                .order_by(Storage.created_at.desc())\
                .paginate(page=content['page'], per_page=content['per_page'], error_out=False)
        storage_dtos = [
            StorageDTO(
                id=storage.id,
                pray_id=storage.pray_id,
                user_id=storage.user_id,
                pray_cnt=storage.pray_cnt,
                deadline=storage.deadline,
                created_at=storage.created_at,
                pray=storage.pray
            ).history()
            for storage in storages.items
        ]
        res = {
			'res' : storage_dtos,
			'total' : storages.total,
			'has_prev': storages.has_prev,
			'has_next': storages.has_next,
			'prev_num': storages.prev_num,
			'next_num': storages.next_num,
			'page': storages.page,
			'pages': storages.pages,
			'per_page': storages.per_page,
		}
        return (res)


class PrayService:
    def create_pray(target, title, deadline) -> PrayDTO:
        try:
            pray_dto = PrayDTO(
                target=target,
                title=title,
                user_id=g.user_id,
            )
            pray_dto.save()
            return StorageService.create_storage(pray_dto, deadline)
        except Exception:
            raise PrayFail('create pray error')
        

    def update_pray(content, storage_id) -> PrayDTO:
        try:
            storage = Storage.query.filter_by(id=storage_id, user_id=g.user_id).filter(Storage.deleted_at == None).first()
            if not storage:
                raise PrayFail('pray not found')
            shared_storage = Share.query.filter_by(pray_id=storage.pray_id).all()
            if len(shared_storage) > 1:
                raise PrayFail('can not update shared pray')
            elif str(storage.pray.user_id) != str(g.user_id):
                raise PrayFail('can not update other user pray')
            pray = Pray.query.filter_by(id=storage.pray_id).first()
            if 'target' in content:
                pray.target = content['target']
            if 'title' in content:
                pray.title = content['title']
            if 'deadline' in content:
                pray.deadline = content['deadline']
            db.session.commit()
            return StorageService.get_storage(storage_id)

        except Exception:
            raise PrayFail('update pray error')
            
