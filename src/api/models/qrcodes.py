from api.utils.database import db, ma
from datetime import datetime
import enum

class Choices(enum.Enum):
  DEMANDEUR = 'Demandeur'
  GROUPE = 'Groupe'

class Qrcode(db.Model):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  owner = db.Column(db.Enum(Choices))
  owner_id = db.Column(db.Integer)
  url = db.Column(db.String(255)) 
  created_at = db.Column(db.DateTime, default=datetime.utcnow())
