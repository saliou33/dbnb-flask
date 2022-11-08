import datetime
import os


class Config(object):
    DEBUG = False
    TESTING = False
    SQLACHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=3)
    JWT_SECRET_KEY = '336f3f81c6644058b593d9339153b7ca'
    UPLOAD_EXTENSIONS = ['xlsx', 'csv']
    UPLOAD_PATH = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'data')
    FERNET_KEY = 'juzm4Q6T9ao-ElocILKAAVFQZy6vDz1hcYruKDHL-nQ='
    GOOGLE_CREDENTIALS_PATH = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'token.json')
    GOOGLE_FOLDER_ID = '1IlkjFPfkyLHa98aEuIxTvi3Nv3gejj9Z'

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgres://dbnb:dbnb33@localhost:5432/dbnb')\
        .replace("postgres://", "postgresql://", 1)


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQALCHEMY_ECHO = False


class TestingConfig(Config):
    TESTING = True
    SQALCHEMY_ECHO = False
