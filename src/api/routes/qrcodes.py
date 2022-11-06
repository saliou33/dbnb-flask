import traceback
from flask import Blueprint, request
from api.utils.responses import response_with
import api.utils.responses as resp
from api.models.qrcodes import Qrcode, QrcodeSchema
from api.models.demandeurs import Demandeur
from api.models.groupes import Groupe
from marshmallow import ValidationError
from api.config import Config
from cryptography.fernet import Fernet
import zipfile
from io import BytesIO
import uuid
import os
import qrcode

qrcode_routes = Blueprint("qrcode_routes", __name__)


@qrcode_routes.route("/", methods=['GET'])
def get_qrcodes():
    try:
        qrcodes = Qrcode.query.all()
        schema = QrcodeSchema(many=True)
        qrcodes = schema.dump(qrcodes)
        return response_with(resp.SUCCESS_200, value={'qrocdes': qrcodes})

    except Exception as e:
        return response_with(resp.SERVER_ERROR_500)


@qrcode_routes.route("/<int:id>", methods=['GET'])
def get_qrcode(id):
    try:
        schema = QrcodeSchema()
        qrcode = Qrcode.find_by_id(id)
        if not qrcode:
            raise ValidationError(message={'id': 'Demandeur not found'})
        qrcode = schema.dump(qrcode)
    except ValidationError as e:
        return response_with(resp.INVALID_INPUT_422, value={'message': e.messages})
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
        print(key)
        qrcodes.append((str(idx) + ".png", qrcode.make(key)))

    # save file in zip
    zip_file_name = str(uuid.uuid4().hex) + ".zip"
    in_memory = BytesIO()
    img_buffer = BytesIO()

    with zipfile.ZipFile(in_memory, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for filename, data in qrcodes:
            data.save(img_buffer, 'PNG')
            img_buffer.seek(0)
            zip_file.writestr(filename, img_buffer.read())

    with open(os.path.join(Config.UPLOAD_PATH, zip_file_name), "wb") as f:
        f.write(in_memory.getvalue())

    return zip_file_name


@qrcode_routes.route("/", methods=['POST'])
def create_qrcode():
    try:
        data = request.get_json()
        schema = QrcodeSchema(exclude=['id', 'created_at', 'url'])
        fields = schema.load(data)
        bricks = []
        owner = None

        if data['owner'] == 'demandeur':
            owner = Demandeur.find_by_id(data['owner_id'])
        else:
            owner = Groupe.find_by_id(data['owner_id'])

        if not owner:
            raise ValidationError(message={'owner': 'owner with id not found'})

        if data['owner'] == 'demandeur':
            bricks.append(owner)
        else:
            bricks = owner.get_demandeurs()

        zip_file = generate_qrcode(bricks)

    except ValidationError as e:
        print(traceback.format_exc())
        return response_with(resp.INVALID_INPUT_422, value={'message': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)
