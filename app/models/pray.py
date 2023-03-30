from sqlalchemy.dialects.postgresql import UUID
import uuid
from . import db

class Pray(db.Model):
		id = db.Column(db.Integer, primary_key=True)
		userId = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
		target = db.Column(db.String(50), nullable=False)
		title = db.Column(db.Text(), nullable=False)