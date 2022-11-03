from flask import Blueprint
from flask import request
from api.utils.responses import response_with
from api.utils import responses as resp
from api.models.users import User, UserSchema
from api.utils.database import db
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from sqlalchemy import exc

user_routes = Blueprint("user_routes", __name__)

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
      value={'message': 'User create error', 'errors': e.messages})
  except exc.SQLAlchemyError as e:
    return response_with(resp.INVALID_INPUT_422, value={"errors": str(e.orig)})
  except Exception as e:
    print(e)
    return response_with(resp.SERVER_ERROR_500)
 
@user_routes.route('/', methods=['PUT'])
def update_user():
  pass

@user_routes.route('/', methods=['DELETE'])
def delete_user():
  pass

@user_routes.route('/login', methods=['POST'])
def authenticate_user():
  try:
    data = request.get_json()
    current_user = User.find_by_email(data['email'])

    if not current_user:
        return response_with(resp.INVALID_INPUT_422)

    if User.verify_hash(data["password"], current_user.password):
      access_token = create_access_token(identity = data['email'])

      return response_with(resp.SUCCESS_201, 
        value={'message': f'Logged as {current_user.name}', 
        'acces_token': access_token})
    else:
      return response_with(resp.UNAUTHORIZED_403, value={'message': "Incorrect email or password"})
  except Exception as e:
    print(e)
    return response_with(resp.INVALID_INPUT_422)