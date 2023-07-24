from sqlalchemy.dialects.postgresql import UUID
import uuid
from . import db
import datetime

class User(db.Model):
		id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
		uid = db.Column(db.String(100), unique=True, nullable=False)
		password = db.Column(db.String(200), nullable=False)
		name = db.Column(db.String(150), nullable=False)
		gender = db.Column(db.String(10), nullable=False)
		birth = db.Column(db.DateTime(), nullable=False)
		phone = db.Column(db.String(20), unique=True, nullable=False)
		device_token = db.Column(db.String(200), nullable=True)
		created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
		deleted_at = db.Column(db.DateTime(), nullable=True)
		reset_pw = db.Column(db.String(200), nullable=True)

class LocalAuth(db.Model):
		id = db.Column(db.String(100), primary_key=True, nullable=False)
		user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
		password = db.Column(db.String(200), nullable=False)
		user = db.relationship('User', backref='local_auth')

class SocialAuth(db.Model):
		id = db.Column(db.String(100), primary_key=True, nullable=False)
		user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
		social_type = db.Column(db.String(50), nullable=False)
		access_token = db.Column(db.String(200), nullable=True)
		connected_at = db.Column(db.DateTime(), nullable=True)
		user = db.relationship('User', backref='social_auth')

class UserDelete(db.Model):
		reason_id = db.Column(db.Integer, db.ForeignKey('user_delete_reason.id', ondelete='CASCADE'))
		user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
		created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
		reason = db.relationship('UserDeleteReason', backref='user_delete')
		etc = db.Column(db.String(100), nullable=True)
		__table_args__ = (
				db.PrimaryKeyConstraint(reason_id, user_id), {}
		)


class UserDeleteReason(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		reason = db.Column(db.String(100), nullable=False)


class UserNotificationLog(db.Model):
		id = db.Column(db.BigInteger, primary_key=True)
		user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
		user = db.relationship('User', backref='notification')
		content = db.Column(db.String(100), nullable=False)
		notification_id = db.Column(db.Integer, db.ForeignKey('notification.id', ondelete='CASCADE'))
		notification = db.relationship('Notification', backref='notification')
		created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())


class UserNotification(db.Model):
		user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'))
		user = db.relationship('User', backref='user_notification')
		notification_id = db.Column(db.Integer, db.ForeignKey('notification.id', ondelete='CASCADE'))
		notification = db.relationship('Notification', backref='user_notification')
		is_enabled = db.Column(db.Boolean, nullable=False, default=True)
		updated_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
		__table_args__ = (
				db.PrimaryKeyConstraint(user_id, notification_id), {}
		)


class Notification(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		content = db.Column(db.String(100), nullable=False)
		updated_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())