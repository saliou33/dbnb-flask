from api.utils.database import db, ma
from datetime import datetime
from passlib.hash import pbkdf2_sha256 as sha256
from marshmallow import fields, validate, validates, Schema, ValidationError

class User(db.Model):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(100), nullable=False)
  email = db.Column(db.String(120), unique=True, nullable=False)
  tel = db.Column(db.Integer, unique=True)
  password = db.Column(db.String(68), nullable=False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow)

  def __init__(self, name, email, password, tel=None):
    self.name = name
    self.email = email
    self.password = password
    self.tel = tel

  def create(self):
    db.session.add(self)
    db.session.commit()
    return self
  
  @staticmethod
  def generate_hash(password):
    return sha256.hash(password)
  
  @staticmethod
  def verify_hash(password, hash):
    return sha256.verify(password, hash)
  
  @classmethod
  def find_by_email(cls, email):
    return cls.query.filter_by(email = email).first()
  
  def __repr__(self):
    return '<Use %r>' % self.name

class UserSchema(ma.SQLAlchemySchema):
  class Meta:
    model = User
    
  id = ma.auto_field()
  name = fields.Str(required=True)
  email = fields.Email(required=True)
  password = fields.Str(required=True, 
  validate=validate.Length(min=8, max=64))
  tel = fields.Int()
  created_at = ma.auto_field()
  updated_at = ma.auto_field()

class UserSchemaUpdate(Schema):
  class Meta:
    fields = ("id","email", "name", "password", "new_password", "confirm_password", "tel")

  id = fields.Int(required=True)
  password = fields.Str(required=True)
  new_password = fields.Str(validate=validate.Length(min=8, max=64))
  confirm_password = fields.Str()
  email = fields.Email(required=True)
  name = fields.Str(validate=validate.Length(max=100))
  tel = fields.Str(validate=validate.Length(min=9))


