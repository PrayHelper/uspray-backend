from datetime import timedelta
import datetime
import uuid
from app.models.pray import Pray, Share
from app.models import db
from flask import g
from sqlalchemy import and_, not_
from app.utils.error_handler import ShareError
from app.utils.pray import PrayDTO, StorageService
from app.models.pray import Storage



class ShareDTO:
    receipt_id: uuid
    storage_id: int
    shared_at: datetime
    pray: PrayDTO

    def __init__(self, receipt_id, storage_id, storage=None, shared_at=None):
        self.receipt_id = receipt_id
        self.storage_id = storage_id
        self.storage = storage
        self.shared_at = shared_at
        if not receipt_id:
            raise ShareError('receipt_id is required')
        if not storage_id:
            raise ShareError('pray_id is required')

    def __repr__(self):
        return {
            'pray_id': self.storage_id,
            'share_name': self.storage.user.name,
            'target': self.storage.pray.target,
            'title': self.storage.pray.title,
            'shared_at': self.shared_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def to_model(self) -> Share:
        return Share(
            receipt_id=self.receipt_id,
            storage_id=self.storage_id
        )
    
    def save(self):
        try:
            share = self.to_model()
            db.session.add(share)
            db.session.commit()
            self.shared_at = share.created_at
            self.storage = share.storage

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

class ShareService:
    def get_pray(storage_id): 
        pray = Storage.query.filter_by(id=storage_id).first()
        if pray is None or str(pray.user_id) != g.user_id:
            raise ShareError('기도제목이 존재하지 않습니다.')
        return pray

    def share_pray(prayList):
        for pray_id in prayList:
          pray = Storage.query.filter_by(id=pray_id).first()
          if pray is None or pray.user_id == g.user_id:
                raise ShareError('공유할 수 없는 기도제목입니다.')
          if Share.query.filter_by(receipt_id=g.user_id, storage_id=pray_id).first() is not None:
                raise ShareError('이미 공유받은 기도제목입니다.')
          try:
              share = ShareDTO(receipt_id=g.user_id, storage_id=pray_id)
              share.save()
          except: 
            raise ShareError('공유받기에 실패했습니다.')
        return [ ShareService.get_share_pray(pray_id) for pray_id in prayList ]
    
    def get_share_list():
        fifteen_days_ago = datetime.datetime.now() - timedelta(days=15)

        share_list = db.session.query(Share, Storage).join(Storage, Storage.id == Share.storage_id).filter(
            Share.receipt_id == g.user_id,
            Storage.deadline > fifteen_days_ago,
            Share.deleted_at == None
        ).all()

        return [ ShareDTO(share.receipt_id, share.storage_id, share.storage, share.created_at).__repr__() for (share, storage) in share_list ]
    
    def get_share_pray(storage_id):
        share = Share.query.filter_by(storage_id=storage_id).first()
        if share is None:
            raise ShareError('공유받은 기도제목이 아닙니다.')
        return ShareDTO(share.receipt_id, share.storage_id, share.storage, share.created_at).__repr__()
    
    def save_storage(storage_list):
        result = []
        for storage_id in storage_list:
            share = Share.query.filter_by(storage_id=storage_id).first()
            if share is None:
                raise ShareError('공유받은 기도제목이 아닙니다.')
            storage = Storage.query.filter_by(id=storage_id).first()
            if storage is None:
                raise ShareError('존재하지 않는 기도제목입니다.')
            result.append(StorageService.create_storage(storage.pray, storage.deadline + datetime.timedelta(days=15)))
        return result
        

    def delete_share_list(storage_list):
        for storage_id in storage_list:
            share = Share.query.filter_by(storage_id=storage_id).filter_by(receipt_id=g.user_id).first()
            if share is None:
                raise ShareError('공유받은 기도제목이 아닙니다.')
            storage = Storage.query.filter_by(user_id=share.receipt_id).filter_by(pray_id=share.storage.pray_id).first()
            if storage:
                raise ShareError('저장한 기도제목은 삭제할 수 없습니다.')
            share.deleted_at = datetime.datetime.now()
        db.session.commit()
        return ShareService.get_share_list()