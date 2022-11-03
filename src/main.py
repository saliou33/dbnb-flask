import os
from flask import Flask
from flask import jsonify
from api.utils.database import db, ma
from flask_jwt_extended import JWTManager
from api.config import *
from api.utils.responses import response_with
from api.utils import responses as resp
from api.routes.users import user_routes

app = Flask(__name__)

#  environment variables
if os.environ.get('WORK_ENV') == 'PROD':
  app_config = ProductionConfig
elif os.environ.get('WORK_ENV') == 'TEST':
  app_config = TestingConfig
else:
  app_config = DevelopmentConfig

# app routes
app.register_blueprint(user_routes, url_prefix='/api/users')

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
jwt = JWTManager(app)
db.init_app(app)
ma.init_app(app)
with app.app_context():
  db.create_all()


if __name__ == "__main__":
  app.run(port=5000, host='0.0.0.0', use_reloader=False)