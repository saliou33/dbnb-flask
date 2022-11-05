from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.demandeurs import Demandeur, DemandeurSchema, DemandeurGetSchema,\
    DemandeurUpdateSchema
from api.utils.database import db
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from sqlalchemy import exc
from sqlalchemy.sql import _or
import pandas as pd
import numpy as np
import traceback

# Demandeur routes
demandeur_routes = Blueprint("demandeur_routes", __name__)


@demandeur_routes.route("/", methods=['GET'])
def get_demandeurs():
    try:
        data = Demandeur.query.all()
        demandeur_schema = DemandeurSchema(many=True)
        demandeurs = demandeur_schema.dump(data)
        return response_with(resp.SUCCESS_200, value={'demandeurs', demandeurs})
    except Exception as e:
        print(e)


@demandeur_routes.route("/<int:id>", methods=['GET'])
def get_demandeur(id):
    try:
        data = request.get_json()
        demandeur_schema = DemandeurGetSchema.load(data)
        current_demandeur = Demandeur.find_by_id(data['id'])
        if not current_demandeur:
            raise ValidationError(message={'id': 'Demandeur not found'})
        demandeur = demandeur_schema.dump(current_demandeur)

        return response_with(resp.SUCCESS_200, value={'demandeur': demandeur})
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'message': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@demandeur_routes.route("/", methods=['POST'])
def create_demandeur():
    try:
        data = request.get_json()
        demandeur_schema = DemandeurSchema()
        demandeur = demandeur_schema.load(data)
        new_demandeur = Demandeur(**demandeur)
        new_demandeur.create()

        return response_with(resp.SUCCESS_200, value={'message': 'Demandeur sucessfully created'})
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'message': e.messages})
    except exc.SQLAlchemyError:
        return response_with(resp.INVALID_INPUT_422, value={"errors": str(e.orig)})
    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)


def read_file(file):
    type = {'CNI': np.str0,
            'Téléphone': np.str0,
            'Numéro dépôt Courrier': np.str0}
    allowed_extensions = ['xlsx', 'csv']

    try:
        if file:
            extension = file.filename.split('.')[-1]
            if extension in allowed_extensions:
                if extension == 'csv':
                    return pd.read_csv(file, headers=True, dtype=type)
                else:
                    return pd.read_excel(file, dtype=type)
            else:
                raise ValidationError(
                    message={'file': 'Only .xlsx or .csv files allowed'})

        else:
            raise ValidationError(message={'file': 'File not found'})
    except Exception as e:
        raise ValidationError(message='Invalid File')


@demandeur_routes.route("/upload_check", methods=['POST'])
def upload_check_demander():
    try:
        file = request.files['file']
        data = read_file(file)
        errors = []
        for index, row in data.iterrows():
            demandeur = Demandeur.query.filter(
                _or(Demandeur.cni == row['CNI'], Demandeur.tel == row['Téléphone'])).first()
            if demandeur:
                errors.append(row.to_dict())

        return errors
    except Exception as e:
        print(traceback.format_exc())


@demandeur_routes.route("/upload", methods=['POST'])
def upload_demandeur():
    try:
        file = request.files['file']
        data = read_file(file)

        print(data.head())
        return response_with(resp.SUCCESS_200)
    except ValidationError as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@demandeur_routes.route("/", methods=['PUT'])
def update_demandeur():
    try:
        data = request.get_json()
        demandeur_schema = DemandeurUpdateSchema()
        demandeur = demandeur_schema.load(data)
        current_demandeur = Demandeur.find_by_id(data['id'])

        if not current_demandeur:
            raise ValidationError(message={'id': 'Demandeur not found'})

        Demandeur.query.upate(current_demandeur, demandeur)
        db.session.commit()

    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'message': e.messages})
    except exc.SQLAlchemyError:
        return response_with(resp.INVALID_INPUT_422, value={"errors": str(e.orig)})
    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)


@demandeur_routes.route("/", methods=['DELETE'])
def delete_demandeur():
    pass
