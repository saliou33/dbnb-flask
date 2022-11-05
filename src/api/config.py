import uuid
class Config(object):
  DEBUG = False
  TESTING = False
  SQLACHEMY_TRACK_MODIFICATIONS = False
  SECRET_KEY = uuid.uuid4().hex
  UPLOAD_EXTENSIONS = ['xlxs', 'csv']

class ProductionConfig(Config):
  SQLALCHEMY_DATABASE_URI = ''

class DevelopmentConfig(Config):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = 'postgresql://dbnb:dbnb33@localhost:5432/dbnb'
  SQALCHEMY_ECHO = False

class TestingConfig(Config):
  TESTING = True
  SQLALCHEMY_DATABASE_URI = 'postgresql://dbnb:dbnb33@localhost:5432/dbnb'
  SQALCHEMY_ECHO = False
