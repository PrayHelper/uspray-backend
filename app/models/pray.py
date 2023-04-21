from sqlalchemy.dialects.postgresql import UUID
from . import db
import datetime

class Pray(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
		target = db.Column(db.String(50), nullable=False)
		title = db.Column(db.Text(), nullable=False)
		user = db.relationship('User', backref=db.backref('pray_set'))


class Storage(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		pray_id = db.Column(db.Integer, db.ForeignKey('pray.id', ondelete='CASCADE'), nullable=False)
		pray = db.relationship('Pray', backref=db.backref('storage'))
		user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
		pray_cnt = db.Column(db.Integer, nullable=False, default=0)
		deadline = db.Column(db.DateTime(), nullable=False)
		created_at = db.Column(db.DateTime(), nullable=False, default=datetime.datetime.now())
		user = db.relationship('User', backref=db.backref('storage_set'))


class Share(db.Model):
    pray_id = db.Column(db.Integer, db.ForeignKey('pray.id', ondelete='CASCADE'), nullable=False)
    pray = db.relationship('Pray', backref=db.backref('pray'))
    receipt_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True)
    __table_args__ = (
        db.PrimaryKeyConstraint(pray_id, receipt_id), {}
    )