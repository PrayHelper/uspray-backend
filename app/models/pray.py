from sqlalchemy.dialects.postgresql import UUID
from . import db
import datetime

class Pray(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
		target = db.Column(db.String(50), nullable=False)
		title = db.Column(db.Text(), nullable=False)
		user = db.relationship('User', backref=db.backref('pray_set'))
		is_shared = db.Column(db.Boolean(), nullable=False, default=False)

class Storage(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		pray_id = db.Column(db.Integer, db.ForeignKey('pray.id', ondelete='CASCADE'), nullable=False)
		pray = db.relationship('Pray', backref=db.backref('storage'))
		user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
		pray_cnt = db.Column(db.Integer, nullable=False, default=0)
		deadline = db.Column(db.DateTime(), nullable=False)
		created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now)
		user = db.relationship('User', backref=db.backref('storage_set'))
		deleted_at = db.Column(db.DateTime(), nullable=True)

class Share(db.Model):
    storage_id = db.Column(db.Integer, db.ForeignKey('storage.id', ondelete='CASCADE'), nullable=False)
    storage = db.relationship('Storage', backref=db.backref('share', cascade="delete"))
    receipt_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    pray_id = db.Column(db.Integer, db.ForeignKey('pray.id', ondelete='CASCADE'), nullable=False)
    pray = db.relationship('Pray', backref=db.backref('share_set'))
    __table_args__ = (
        db.PrimaryKeyConstraint(storage_id, receipt_id, pray_id), {}
    )
    
class Complete(db.Model):
		storage_id = db.Column(db.Integer, db.ForeignKey('storage.id', ondelete='CASCADE'), nullable=False)
		storage = db.relationship('Storage', backref=db.backref('complete', cascade="delete"))
		user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
		user = db.relationship('User', backref=db.backref('complete_set'))
		created_at = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
		__table_args__ = (
				db.PrimaryKeyConstraint(storage_id, user_id), {}
		)