from api.utils.database import db, ma
from datetime import datetime
from passlib.hash import md5_crypt
from marshmallow import fields, validate, validates, Schema, ValidationError
import numpy as np


class Demandeur(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    nom = db.Column(db.String(100), nullable=False)
    prenom = db.Column(db.String(100), nullable=False)
    tel = db.Column(db.String(25), unique=True, nullable=False)
    cni = db.Column(db.String(100), unique=True, nullable=False)
    numero_depot = db.Column(db.String(50))
    categorie_sociale = db.Column(db.String(100))
    created_at = db.Column(db.String(100))
    is_selected = db.Column(db.Boolean, default=False)
    selection_expiration_date = db.Column(
        db.DateTime, default=datetime.utcnow())

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def __repr__(self):
        return '<Demandeur %r %r>' % self.nom, self.prenom


class DemandeurSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Demandeur

    id = ma.auto_field()
    nom = fields.Str(required=True)
    prenom = fields.Str(required=True)
    cni = fields.Str(required=True)
    tel = fields.Str(required=True, validate=validate.Regexp(
        "^\\+?[1-9][0-9]{7,14}$"))
    numero_depot = fields.Str()
    categorie_sociale = fields.Str()
    is_selected = ma.auto_field()
    selection_expiration_date = ma.auto_field()


class DemandeurUpdateSchema(Schema):
    class Meta:
        fields = ('id', 'nom', 'prenom', 'cni',
                  'numero_depot', 'categorie_sociale', 'tel')

    id = fields.Int(required=True)
    nom = fields.Str()
    prenom = fields.Str()
    cni = fields.Str()
    categorie_sociale = fields.Str()
    tel = fields.Str(validate=validate.Regexp("^\\+?[1-9][0-9]{7,14}$"))


class DemandeurMeta():
    columns = {'CNI': np.str0,
               'Téléphone': np.str0,
               'Numéro dépôt Courrier': np.str0,
               'Catégorie Sociale': np.str0,
               'Prénom': np.str0,
               'Nom': np.str0}

    mapping = {'cni': 'CNI',
               'tel': 'Téléphone',
               'numero_depot': 'Numéro dépôt Courrier',
               'categorie_sociale': 'Catégorie Sociale',
               'prenom': 'Prénom',
               'nom': 'Nom'}
