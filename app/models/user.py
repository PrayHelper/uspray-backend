from sqlalchemy.dialects.postgresql import UUID
import uuid
from app import db

class User(db.Model):
		id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
		uid = db.Column(db.String(100), unique=True, nullable=False)
		password = db.Column(db.String(200), nullable=False)
		name = db.Column(db.String(150), nullable=False)
		gender = db.Column(db.String(10), nullable=False)
		birth = db.Column(db.DateTime(), nullable=False)
		phone = db.Column(db.String(20), unique=True, nullable=False)