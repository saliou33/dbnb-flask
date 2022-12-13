from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.users import User, UserSchema, UserUpdateSchema
from api.utils.database import db
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.config import Config
from sqlalchemy import exc
import datetime
import traceback

# Demandeur routes
user_routes = Blueprint("user_routes", __name__)


@user_routes.route('/', methods=['GET'])
@jwt_required()
def get_users():
    users = User.query.all()
    user_schema = UserSchema(many=True, exclude=['password'])
    users = user_schema.dump(users)
    return response_with(resp.SUCCESS_200, value={'users': users})


@user_routes.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_user(id):
    user = User.query.filter_by(id=id)
    user_schema = UserSchema(exclude=['password'])
    user = user_schema.dump(user)
    return response_with(resp.SUCCESS_200, value={'user': user})


@user_routes.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        user_schema = UserSchema()
        user = User(**user_schema.load(data))
        user.password = User.generate_hash(user.password)
        result = user_schema.dump(user.create())
        return response_with(resp.SUCCESS_201)
    except ValidationError as e:
        print(traceback.format_exc())
        return response_with(resp.INVALID_INPUT_422,
                             value={'msg': e.messages})
    except exc.SQLAlchemyError as e:
        print(traceback.format_exc())
        return response_with(resp.INVALID_INPUT_422, value={'msg': str(e.orig)})
    except Exception as e:
        print(e)
        return response_with(resp.SERVER_ERROR_500)


@user_routes.route('/', methods=['PUT'])
@jwt_required()
def update_user():
    try:
        data = request.get_json()
        user_schema = UserUpdateSchema()
        user = user_schema.load(data)
        #  check if user exit
        current_user = User.query.filter_by(id=user['id']).first()
        if not current_user:
            raise ValidationError(message='L\'utilsateur n\'existe pas')

        # check password
        if not User.verify_hash(user['password'], current_user.password):
            raise ValidationError(
                {"password": "Le mot de passe est incorrect"})

        # validate new password
        if 'new_password' in user and user['new_password']:
            if 'confirm_password' in user:
                if user['new_password'] == user['confirm_password']:
                    current_user.password = User.generate_hash(
                        user['new_password'])
                else:
                    raise ValidationError(
                        {"new_password": "Les mots de passe ne corresponsdent pas"})
            else:
                raise ValidationError(
                    {"confirm_password": "Le champs confimer mot de passe est nécessaire"})
        elif 'confirm_password' in user:
            raise ValidationError(
                {"new_password": "Les mots de passe ne corresponsdent pas"})

        # update user
        if 'tel' in user:
            current_user.tel = user['tel']
        current_user.email = user['email']
        current_user.updated_at = datetime.datetime.now()
        db.session.commit()

        return response_with(resp.SUCCESS_200, value={'msg': 'Mise à jour effectué avec succés'})
    except ValidationError as e:
        print(traceback.format_exc())
        return response_with(resp.INVALID_INPUT_422,
                             value={'msg': 'Erreur Modification Utilisateur', 'errors': e.messages})
    except exc.SQLAlchemyError as e:
        print(traceback.format_exc())
        return response_with(resp.INVALID_INPUT_422, value={"errors": str(e.orig)})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@user_routes.route("/<int:id>", methods=['DELETE'])
@jwt_required()
def delete_user():
    try:
        user = User.find_by_id(id)
        if not user:
            raise ValidationError(message='L\'utilisateur n\'éxiste pas')
        db.session.delete(user)

        return response_with(resp.SUCCES_204)
    except ValidationError as e:
        print(traceback.format_exc())
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@user_routes.route('/login', methods=['POST'])
def authenticate_user():
    try:
        data = request.get_json()
        schema = UserUpdateSchema(only=('email', 'password'))
        schema.load(data)
        current_user = User.find_by_email(data['email'])

        if not current_user:
            return response_with(resp.INVALID_INPUT_422, message='Email ou Mot de passe Incorrect')

        if User.verify_hash(data["password"], current_user.password):
            access_token = create_access_token(
                identity=data['email'])

            return response_with(resp.SUCCESS_201,
                                 value={'msg': f'Connecté en tant que {current_user.name}',
                                        'token': access_token, 'user_id': current_user.id})
        else:
            return response_with(resp.UNAUTHORIZED_403, value={'msg': "Email ou Mot de passe Incorrect"})
    except ValidationError as e:
        print(traceback.format_exc())
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@user_routes.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    try:
        email = get_jwt_identity()
        user = User.find_by_email(email)
        if user:
            return response_with(resp.SUCCESS_200)
        else:
            return response_with(resp.UNAUTHORIZED_403, message="Votre Session a expiré")
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)
