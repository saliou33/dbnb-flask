from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.groupes import Groupe, GroupeSchema
from api.models.demandeurs import Demandeur
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from sqlalchemy import exc
import traceback

groupe_routes = Blueprint("groupe_routes", __name__)


@groupe_routes.route("/", methods=['GET'])
@jwt_required()
def get_groupes():
    try:
        data = Groupe.query.all()
        groupe_schema = GroupeSchema(many=True)
        groupes = groupe_schema.dump(data)

        return response_with(resp.SUCCESS_200, value={'groupes': groupes})
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'message': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@groupe_routes.route("/<int:id>", methods=['GET'])
@jwt_required()
def get_groupe(id):
    try:
        data = request.get_json()
        groupe_schema = GroupeSchema()
        groupe = Groupe.find_by_id(data['id'])
        if not groupe:
            raise ValidationError(message={'id': 'Groupe not found'})
        groupe = groupe_schema.dump(groupe)

        return response_with(resp.SUCCESS_200, value={'groupe': groupe})
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'message': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@groupe_routes.route("/", methods=['POST'])
@jwt_required()
def create_groupe():
    try:
        data = request.get_json()
        groupe_schema = GroupeSchema(exclude=['created_at', 'id'])

        groupe = groupe_schema.load(data)
        new_groupe = Groupe(**groupe)
        for user_id in new_groupe.demandeurs:
            demandeur = Demandeur.find_by_id(user_id)
            if not demandeur:
                raise ValidationError(
                    message={'demandeurs': f"Demandeur of id({user_id}) is not found"})
        new_groupe.create()

        return response_with(resp.SUCCESS_200, value={'message': 'Groupe sucessfylly created'})

    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'message': e.messages})
    except exc.SQLAlchemyError as e:
        return response_with(resp.INVALID_INPUT_422, value={"errors": str(e.orig)})
    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)
