from flask import Blueprint, request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.users import User, UserSchema, UserUpdateSchema
from api.utils.database import db
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
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
        return response_with(resp.INVALID_INPUT_422,
                             value={'msg': 'User create error', 'errors': e.messages})
    except exc.SQLAlchemyError as e:
        return response_with(resp.INVALID_INPUT_422, value={"errors": str(e.orig)})
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
            raise ValidationError({"id": "User is not found"})

        # check password
        if not User.verify_hash(user['password'], current_user.password):
            raise ValidationError({"password": "Password is not correct"})

        # validate new password
        if 'new_password' in user and user['new_password']:
            if 'confirm_password' in user:
                if user['new_password'] == user['confirm_password']:
                    current_user.password = User.generate_hash(
                        user['new_password'])
                else:
                    raise ValidationError(
                        {"new_password": "Password mismatch"})
            else:
                raise ValidationError(
                    {"confirm_password": "Field is required for confirming password"})
        elif 'confirm_password' in user:
            raise ValidationError({"new_password": "Password mistmatch"})

        # update user
        if 'tel' in user:
            current_user.tel = user['tel']
        current_user.email = user['email']
        current_user.updated_at = datetime.datetime.now()
        db.session.commit()

        return response_with(resp.SUCCESS_200, value={'msg': 'User updated successfully'})
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422,
                             value={'msg': 'User update error', 'errors': e.messages})
    except exc.SQLAlchemyError as e:
        return response_with(resp.INVALID_INPUT_422, value={"errors": str(e.orig)})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)


@user_routes.route("/", methods=['DELETE'])
@jwt_required()
def delete_user():
    try:
        data = request.get_json()

        if 'id' not in data:
            raise ValidationError(message={'id': 'key id not found'})

        user = User.find_by_id(id)
        if not user:
            raise ValidationError(message={'id': 'user not found'})
        db.session.delete(user)

        return response_with(resp.SUCCES_204)
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)


@user_routes.route('/login', methods=['POST'])
def authenticate_user():
    try:
        data = request.get_json()
        current_user = User.find_by_email(data['email'])

        if not current_user:
            return response_with(resp.INVALID_INPUT_422)

        if User.verify_hash(data["password"], current_user.password):
            access_token = create_access_token(identity=data['email'])

            return response_with(resp.SUCCESS_201,
                                 value={'msg': f'Logged as {current_user.name}',
                                        'acces_token': access_token})
        else:
            return response_with(resp.UNAUTHORIZED_403, value={'msg': "Incorrect email or password"})
    except Exception as e:
        print(e)
        return response_with(resp.INVALID_INPUT_422)
