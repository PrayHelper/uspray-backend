import base64
from datetime import timedelta
import datetime
import uuid
from app.models.pray import Pray, Share
from app.models import db
from flask import g
from app.api.utils import send_push_notification
from sqlalchemy import and_, not_, select
from app.utils.error_handler import ShareError
from app.utils.pray import PrayDTO, StorageService
from app.models.pray import Storage



class ShareDTO:
    receipt_id: uuid
    storage_id: int
    shared_at: datetime
    pray: PrayDTO
    pray_id: int

    def __init__(self, receipt_id, storage_id, pray_id, storage=None, shared_at=None):
        self.receipt_id = receipt_id
        self.storage_id = storage_id
        self.pray_id = pray_id
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
            'target': base64.b64decode(self.storage.pray.target).decode('utf-8'),
            'title': base64.b64decode(self.storage.pray.title).decode('utf-8'),
            'shared_at': self.shared_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def to_model(self) -> Share:
        return Share(
            receipt_id=self.receipt_id,
            storage_id=self.storage_id,
            pray_id=self.pray_id
        )
    
    def save(self):
        try:
            share = self.to_model()
            db.session.add(share)
            db.session.commit()
            self.shared_at = share.created_at
            self.storage = share.storage
            self.pray = share.pray

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
          pray = Storage.query.filter_by(id=pray_id).order_by(Storage.created_at).first()
          if pray is None or pray.user_id == g.user_id or pray.deleted_at is not None:
                raise ShareError('공유할 수 없는 기도제목입니다.')
          shared_pray = Share.query.filter_by(receipt_id=g.user_id, storage_id=pray_id).first()
          if shared_pray is not None:
                    if shared_pray.deleted_at is None:
                        raise ShareError('이미 공유받은 기도제목입니다.')
                    else:
                        shared_pray.deleted_at = None
                        db.session.commit()
                        pray.pray.is_shared = True
                        db.session.commit()
                        continue
          else:
            try:
                share = ShareDTO(receipt_id=g.user_id, storage_id=pray_id, pray_id=pray.pray_id)
                share.save()
                pray.pray.is_shared = True
                db.session.commit()
            except: 
                raise ShareError('공유받기에 실패했습니다.')
        return [ ShareService.get_share_pray(pray_id) for pray_id in prayList ]
    
    def get_share_list():
        fifteen_days_ago = datetime.datetime.now() - timedelta(days=15)

        subq = select(Storage.pray_id).where((Storage.user_id == g.user_id)).subquery()
        share_list = Share.query.filter(Share.receipt_id == g.user_id).filter(not_(Share.pray_id.in_(select(subq)))).filter(Share.deleted_at==None, Share.created_at > fifteen_days_ago).order_by(Share.created_at.desc()).all()
        return [ ShareDTO(share.receipt_id, share.storage_id, share.pray_id, share.storage, share.created_at).__repr__() for share in share_list ]
    
    def get_share_pray(storage_id):
        share = Share.query.filter_by(storage_id=storage_id).first()
        if share is None:
            raise ShareError('공유받은 기도제목이 아닙니다.')
        return ShareDTO(share.receipt_id, share.storage_id, share.pray_id, share.storage, share.created_at).__repr__()
    
    def save_storage(storage_list):
        result = []
        for storage_id in storage_list:
            share = Share.query.filter_by(storage_id=storage_id).first()
            if share is None:
                raise ShareError('공유받은 기도제목이 아닙니다.')
            storage = Storage.query.filter_by(id=storage_id).order_by(Storage.created_at).first()
            if storage is None:
                raise ShareError('존재하지 않는 기도제목입니다.')
            if storage.pray.user.device_token:
                send_push_notification('💌', '누군가가 당신의 기도제목을 저장했어요', [storage.pray.user.device_token], {})
            result.append(StorageService.create_storage(storage.pray, datetime.datetime.now() + datetime.timedelta(days=15)))
        return result
        

    def delete_share_list(storage_list):
        for storage_id in storage_list:
            share = Share.query.filter_by(storage_id=storage_id).filter_by(receipt_id=g.user_id).first()
            if share is None:
                raise ShareError('공유받은 기도제목이 아닙니다.')
            storage = Storage.query.filter_by(user_id=share.receipt_id).filter_by(pray_id=share.pray_id).first()
            if storage:
                raise ShareError('저장한 기도제목은 삭제할 수 없습니다.')
            share.deleted_at = datetime.datetime.now()
        db.session.commit()
        return ShareService.get_share_list()