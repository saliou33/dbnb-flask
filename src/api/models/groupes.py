from api.utils.database import ma, db
from sqlalchemy.dialects import postgresql
from datetime import datetime

class Groupe(db.Model):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  demandeurs = db.Column(postgresql.ARRAY(db.Integer))
  created_at = db.Column(db.Datetime, default=datetime.utcnow())

  def create(self):
    db.session.add(self)
    db.session.commit()

class GroupeSchema(ma.SQLAlchemyAutoSchema):
  class Meta:
    model = Groupe
  
  id = ma.auto_field()
  demandeurs = ma.auto_field()