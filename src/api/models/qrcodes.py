from api.utils.database import db, ma
from datetime import datetime
from marshmallow import fields, validate
import enum


class Choices(enum.Enum):
    DEMANDEUR = 'demandeur'
    GROUPE = 'groupe'


class Qrcode(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Enum(Choices), nullable=False)
    owner_id = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    def create(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, id):
        cls.query.filter_by(id=id).first()


class QrcodeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Qrcode

    id = ma.auto_field()
    owner = fields.Str(required=True, validate=validate.OneOf(
        (Choices.DEMANDEUR.value, Choices.GROUPE.value)))
    owner_id = ma.auto_field()
    url = ma.auto_field()
    created_at = ma.auto_field()
