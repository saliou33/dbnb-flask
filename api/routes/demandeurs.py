from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.demandeurs import Demandeur, \
    DemandeurSchema, DemandeurUpdateSchema, DemandeurMeta
from api.models.groupes import GroupeSchema
from api.config import Config
from api.utils.database import db
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from dateutil.relativedelta import relativedelta
from datetime import datetime
from sqlalchemy import exc
from sqlalchemy.sql import or_
import pandas as pd
import traceback

# Demandeur routes
demandeur_routes = Blueprint("demandeur_routes", __name__)


@demandeur_routes.route("/", methods=['GET'])
@jwt_required()
def get_demandeurs():
    try:
        data = Demandeur.query.all()
        schema = DemandeurSchema(many=True)
        demandeurs = schema.dump(data)

        return response_with(resp.SUCCESS_200, value={'demandeurs': demandeurs})
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@demandeur_routes.route("/<int:id>", methods=['GET'])
@jwt_required()
def get_demandeur(id):
    try:
        schema = DemandeurSchema()
        demandeur = Demandeur.find_by_id(id)
        if not demandeur:
            raise ValidationError(message={'id': 'Demandeur not found'})
        demandeur = schema.dump(demandeur)

        return response_with(resp.SUCCESS_200, value={'demandeur': demandeur})
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)


@demandeur_routes.route("/select", methods=['POST'])
@jwt_required()
def select_demandeur():
    try:
        data = request.get_json()
        schema = GroupeSchema(exclude=['id'])
        schema.load(data)

        for idx in data['demandeurs']:
            demandeur = Demandeur.find_by_id(idx)
            if demandeur and demandeur.is_selected == False:
                demandeur.is_selected = True
                demandeur.selection_expiration_date = datetime.utcnow() + relativedelta(years=1)

        db.session.commit()
        return response_with(resp.SUCCESS_200, value={'msg': 'Demandeurs sucessfully selected'})
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@demandeur_routes.route("/deselect", methods=['POST'])
@jwt_required()
def deselect_demandeur():
    try:
        data = request.get_json()
        schema = GroupeSchema(exclude=['id'])
        schema.load(data)

        for idx in data['demandeurs']:
            demandeur = Demandeur.find_by_id(idx)
            if demandeur and demandeur.is_selected == True:
                demandeur.is_selected = False
                demandeur.selection_expiration_date = None

        db.session.commit()
        return response_with(resp.SUCCESS_200, value={'msg': 'Demandeurs sucessfully deselected'})
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@demandeur_routes.route("/", methods=['POST'])
@jwt_required()
def create_demandeur():
    try:
        data = request.get_json()
        schema = DemandeurSchema()
        demandeur = schema.load(data)
        demandeur = Demandeur(**demandeur)
        demandeur.create()

        return response_with(resp.SUCCESS_200, message='Demandeur sucessfully created')
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except exc.SQLAlchemyError as e:
        return response_with(resp.INVALID_INPUT_422, value={"errors": str(e.orig)})
    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)


def read_file(file):
    columns = DemandeurMeta.columns
    allowed_extensions = Config.UPLOAD_EXTENSIONS
    data = None
    if file:
        extension = file.filename.split('.')[-1]
        if extension in allowed_extensions:
            if extension == 'csv':
                data = pd.read_csv(file, headers=True, dtype=columns)
            else:
                data = pd.read_excel(file, dtype=columns)

            if not set(columns.keys()).issubset(data.columns):

                raise ValidationError(
                    message={'file': 'Missing or Invalid Column Name'})

            return data
        else:
            raise ValidationError(
                message={'file': 'Only .xlsx or .csv files allowed'})

    else:
        raise ValidationError(message={'file': 'File not found'})


@demandeur_routes.route("/upload_check", methods=['POST'])
@jwt_required()
def upload_check_demander():
    try:
        file = request.files['file']
        data = read_file(file)
        errors = []
        for index, row in data.iterrows():
            demandeur = Demandeur.query.filter(
                or_(Demandeur.cni == row['CNI'], Demandeur.tel == row['Téléphone'])).first()
            if demandeur:
                errors.append(row.to_dict())

        return response_with(resp.SUCCESS_200, value={'errors': errors})
    except Exception as e:

        return response_with(resp.SERVER_ERROR_500, value={'msg': repr(e)})


@demandeur_routes.route("/upload", methods=['POST'])
@jwt_required()
def upload_demandeur():
    try:
        file = request.files['file']
        data = read_file(file)

        for index, row in data.iterrows():
            params = {k: v for k, v in zip(DemandeurMeta.mapping.keys(), [
                                           row[n] for n in DemandeurMeta.mapping.values()])}
            demandeur = Demandeur(**params)
            db.session.add(demandeur)

        db.session.commit()
        return response_with(resp.SUCCESS_200, value={'msg': 'Demandeurs succesfully created'})
    except ValidationError as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@demandeur_routes.route("/", methods=['PUT'])
@jwt_required()
def update_demandeur():
    try:
        data = request.get_json()
        schema = DemandeurUpdateSchema()
        demandeur = schema.load(data)
        demandeur = Demandeur.find_by_id(data['id'])

        if not demandeur:
            raise ValidationError(message={'id': 'Demandeur not found'})

        Demandeur.query.upate(demandeur, demandeur)
        db.session.commit()

    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except exc.SQLAlchemyError as e:
        return response_with(resp.INVALID_INPUT_422, value={"errors": str(e.orig)})
    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)


@demandeur_routes.route("/", methods=['DELETE'])
@jwt_required()
def delete_demandeur():
    try:
        data = request.get_json()

        if 'id' not in data:
            raise ValidationError(message={'id': 'key id not found'})

        demandeur = Demandeur.find_by_id(id)
        if not demandeur:
            raise ValidationError(message={'demandeur': 'Demandeur not found'})
        db.session.delete(demandeur)

        return response_with(resp.SUCCES_204)
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)
