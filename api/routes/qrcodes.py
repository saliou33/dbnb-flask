from flask import Blueprint, request
from api.utils.responses import response_with
import api.utils.responses as resp
from api.models.qrcodes import Qrcode, QrcodeSchema, QrcodeOwner
from api.models.demandeurs import Demandeur, DemandeurSchema
from api.models.groupes import Groupe
from marshmallow import ValidationError
from api.config import Config
from cryptography.fernet import Fernet
from api.utils.drive import upload_basic
from flask_jwt_extended import jwt_required
from io import BytesIO
import traceback
import tempfile
import zipfile
import qrcode
import uuid

qrcode_routes = Blueprint("qrcode_routes", __name__)

# get qrcodes
@qrcode_routes.route("/", methods=['GET'])
@jwt_required()
def get_qrcodes():
    try:
        qrcodes = Qrcode.query.all()
        schema = QrcodeSchema(many=True)
        qrcodes = schema.dump(qrcodes)
        return response_with(resp.SUCCESS_200, value={'qrcodes': qrcodes})

    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)

# get qrcode(id)
@qrcode_routes.route("/<int:id>", methods=['GET'])
@jwt_required
def get_qrcode(id):
    try:
        schema = QrcodeSchema()
        qrcode = Qrcode.find_by_id(id)
        if not qrcode:
            raise ValidationError(message='Le Qrcode n\'existe pas')
        qrcode = schema.dump(qrcode)
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)


def generate_qrcode(bricks):
    # generate keys
    keys = []
    for brick in bricks:
        keys.append(Fernet(Config.FERNET_KEY).encrypt(
            str(brick.id).encode('utf-8')))

    # create qrcode
    qrcodes = []
    for idx, key in enumerate(keys, start=1):
        qrcodes.append((str(idx) + ".png", qrcode.make(key)))

    # save file in zip
    zip_file_name = str(uuid.uuid4().hex) + ".zip"
    in_memory = BytesIO()

    with zipfile.ZipFile(in_memory, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename, data in qrcodes:
            img_buffer = BytesIO()
            data.save(img_buffer, 'PNG')
            img_buffer.seek(0)
            zip_file.writestr(filename, img_buffer.read())

    temp = tempfile.NamedTemporaryFile(suffix='t_.zip', delete=False)
    temp.write(in_memory.getvalue())
    temp.seek(0)

    # upload file
    file_id = upload_basic(zip_file_name, temp.name)

    return file_id

#check qrcode validity
@qrcode_routes.route("/check", methods=['POST'])
@jwt_required()
def get_demandeur():
    try:
        data = request.get_json()
        if 'code' not in data:
            raise ValidationError(message='Le code est obligatoire')

        demandeur_id = Fernet(Config.FERNET_KEY).decrypt(data['code']).decode('utf-8')
        demandeur = Demandeur.find_by_id(int(demandeur_id))

        if not demandeur:
            raise ValidationError(resp.BAD_REQUEST_400, value={'msg': 'Le demandeur est introuvable;'})

        demandeur = DemandeurSchema().dump(demandeur)
        return response_with(resp.SUCCESS_200, value={'demandeur': demandeur})

    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, message=e.messages)

    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)

#create qrcode
@qrcode_routes.route("/", methods=['POST'])
@jwt_required()
def create_qrcode():
    try:
        data = request.get_json()
        schema = QrcodeSchema(exclude=['id', 'created_at', 'url'])
        schema.load(data)
        bricks = []
        owner = None

        # validation
        if data['owner'] == 'demandeur':
            owner = Demandeur.find_by_id(data['owner_id'])
        else:
            owner = Groupe.find_by_id(data['owner_id'])

        if not owner:
            raise ValidationError(
                message={'owner': 'Le propriétaire est introuvable.'})

        if data['owner'] == 'demandeur':
            bricks.append(owner)
        else:
            bricks = owner.get_demandeurs()

        # generate and uplod qrcode in zipfile
        file_id = generate_qrcode(bricks)

        # save in database
        link = f'https://drive.google.com/file/d/{file_id}/view?usp=share_link'
        qrcode = Qrcode(
            url=link, owner=QrcodeOwner(data['owner']), owner_id=data['owner_id'])
        qrcode.create()
        qrcode = QrcodeSchema().dump(qrcode)

        return response_with(resp.SUCCESS_200, value={'msg': 'Qrcode(s) généré avec succés', 'qrcode': qrcode})

    except ValidationError as e:
        print(traceback.format_exc())
        return response_with(resp.INVALID_INPUT_422, value={'msg': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)
