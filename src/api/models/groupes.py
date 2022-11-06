from api.utils.database import ma, db
from sqlalchemy.dialects import postgresql
from marshmallow import fields, validate
from datetime import datetime
from api.models.demandeurs import Demandeur


class Groupe(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    demandeurs = db.Column(postgresql.ARRAY(db.Integer), default=[])
    created_at = db.Column(db.DateTime, default=datetime.utcnow())

    def create(self):
        db.session.add(self)
        db.session.commit()

    def get_demandeurs(self):
        Demandeur.query.filter_by(Demandeur.id.in_(self.demandeurs)).all()

    @classmethod
    def find_by_id(cls, id):
        cls.query.filter_by(id=id).first()

    def __repr__(self):
        return '<Groupe> %r' % self.id


class GroupeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Groupe

    id = ma.auto_field()
    demandeurs = fields.List(fields.Int(), required=True,
                             validate=validate.Length(min=1))
    created_at = ma.auto_field()
