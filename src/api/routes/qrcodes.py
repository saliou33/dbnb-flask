from flask import Blueprint, request
from api.utils.responses import response_with
import api.utils.responses as resp
from api.models.qrcodes import Qrcode, QrcodeSchema
from api.models.demandeurs import Demandeur
from api.models.groupes import Groupe
from marshmallow import ValidationError
from api.config import Config
from cryptography.fernet import Fernet
from api.utils.drive import upload_basic
from io import BytesIO
import traceback
import zipfile
import qrcode
import uuid
import os

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

    zip_file_path = os.path.join(Config.UPLOAD_PATH, zip_file_name)
    with open(zip_file_path, "wb") as f:
        f.write(in_memory.getvalue())

    return zip_file_name, zip_file_path


@qrcode_routes.route("/", methods=['POST'])
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
            raise ValidationError(message={'owner': 'owner with id not found'})

        if data['owner'] == 'demandeur':
            bricks.append(owner)
        else:
            bricks = owner.get_demandeurs()

        # generate qrcode in zipfile
        zip_name, zip_path = generate_qrcode(bricks)

        # upload file
        file_id = upload_basic(zip_name, zip_path)
        link = f'https://drive.google.com/file/d/{file_id}/view?usp=share_link'

        # save in database
        qrcode = Qrcode(
            url=link, owner=data['owner'], owner_id=data['owner_id'])
        qrcode.create()
        qrcode = QrcodeSchema().dump(qrcode)

        # cleanup
        os.remove(zip_path)

        return response_with(resp.SUCCESS_200, value={'message': 'Qrcodes sucefully generated', 'qrcode': qrcode})

    except ValidationError as e:
        print(traceback.format_exc())
        return response_with(resp.INVALID_INPUT_422, value={'message': e.messages})
    except Exception as e:
        print(traceback.format_exc())
        return response_with(resp.SERVER_ERROR_500)
