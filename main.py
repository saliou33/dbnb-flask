import os
from flask import Flask, jsonify
from flask_cors import CORS
from api.utils.database import db, ma, migrate
from flask_jwt_extended import JWTManager
from api.config import *
from api.utils.responses import response_with
from api.utils import responses as resp
from api.routes.users import user_routes
from api.routes.demandeurs import demandeur_routes
from api.routes.groupes import groupe_routes
from api.routes.qrcodes import qrcode_routes

app = Flask(__name__)

#  environment variables
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_CREDENTIALS_PATH
if os.environ.get('WORK_ENV') == 'PROD':
    app_config = ProductionConfig
elif os.environ.get('WORK_ENV') == 'TEST':
    app_config = TestingConfig
else:
    app_config = DevelopmentConfig

# app routes


@app.route('/', methods=['GET'])
def home():
    return jsonify({'message': 'DBNB FLASK REST API'})


app.register_blueprint(user_routes, url_prefix='/api/users')
app.register_blueprint(demandeur_routes, url_prefix='/api/demandeurs')
app.register_blueprint(groupe_routes, url_prefix='/api/groupes')
app.register_blueprint(qrcode_routes, url_prefix='/api/qrcodes')

# global http response config


@app.after_request
def add_header(response):
    return response


@app.errorhandler(500)
def server_error(e):
    app.logger.info(e)
    return response_with(resp.SERVER_ERROR_500)


@app.errorhandler(400)
def bad_request(e):
    app.logger.info(e)
    return response_with(resp.BAD_REQUEST_400)


@app.errorhandler(404)
def not_found(e):
    app.logger.info(e)
    return response_with(resp.SERVER_ERROR_404)


# app config
app.config.from_object(app_config)
CORS(app)
jwt = JWTManager(app)
db.init_app(app)
ma.init_app(app)
migrate.init_app(app, db)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(port=port, host='0.0.0.0', use_reloader=False)
