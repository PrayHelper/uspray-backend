import datetime
import uuid
from app.models.pray import Pray, Share
from app.models import db
from flask import g
from app.utils.error_handler import ShareError
from app.utils.pray import PrayDTO, StorageService
from app.models.pray import Storage



class ShareDTO:
    receipt_id: uuid
    pray_id: int
    shared_at: datetime
    pray: PrayDTO

    def __init__(self, receipt_id, pray_id, pray=None, shared_at=None):
        self.receipt_id = receipt_id
        self.pray_id = pray_id
        self.pray = pray
        self.shared_at = shared_at
        if not receipt_id:
            raise ShareError('receipt_id is required')
        if not pray_id:
            raise ShareError('pray_id is required')

    def __repr__(self):
        return {
            'pray_id': self.pray_id,
            'share_nickname': self.pray.user.name,
            'target': self.pray.target,
            'title': self.pray.title,
            'shared_at': self.shared_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def to_model(self) -> Share:
        return Share(
            receipt_id=self.receipt_id,
            pray_id=self.pray_id
        )
    
    def save(self):
        try:
            share = self.to_model()
            db.session.add(share)
            db.session.commit()
            self.shared_at = share.created_at
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
    def share_pray(prayList):
        for pray_id in prayList:
          pray = Pray.query.filter_by(id=pray_id).first()
          if pray is None or pray.user_id == g.user_id:
              raise ShareError('공유할 수 없는 기도제목입니다.')
          try:
              share = ShareDTO(receipt_id=g.user_id, pray_id=pray_id)
              share.save()
          except: 
            raise ShareError('공유받기에 실패했습니다.')
        return [ ShareService.get_share_pray(pray_id) for pray_id in prayList ]
    
    def get_share_list():
        share_list = Share.query.filter_by(receipt_id=g.user_id).all()
        return [ ShareDTO(share.receipt_id, share.pray_id, share.pray, share.created_at).__repr__() for share in share_list ]
    
    def get_share_pray(pray_id):
        share = Share.query.filter_by(pray_id=pray_id).first()
        if share is None:
            raise ShareError('공유받은 기도제목이 아닙니다.')
        return ShareDTO(share.receipt_id, share.pray_id, share.pray, share.created_at).__repr__()
    
    def save_storage(pray_id):
        share = Share.query.filter_by(pray_id=pray_id).first()
        if share is None:
            raise ShareError('공유받은 기도제목이 아닙니다.')
        pray = Pray.query.filter_by(id=pray_id).first()
        if pray is None:
            raise ShareError('존재하지 않는 기도제목입니다.')
        pray.user_id = g.user_id
        storage = Storage.query.filter_by(pray_id=pray_id).first()
        if storage is None:
            raise ShareError('기도제목을 저장할 수 없습니다.')
        
        return StorageService.create_storage(pray, storage.deadline)
        