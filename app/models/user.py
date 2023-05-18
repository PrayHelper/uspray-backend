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
		created_at = db.Column(db.DateTime(), nullable=True, default=datetime.datetime.now())
		deleted_at = db.Column(db.DateTime(), nullable=True)


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
