from . import db

class Main(db.Model):
  title = db.Column(db.Text, nullable=False)