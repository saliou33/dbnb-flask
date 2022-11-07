import uuid
import os


class Config(object):
    DEBUG = False
    TESTING = False
    SQLACHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = '336f3f81c6644058b593d9339153b7ca'
    UPLOAD_EXTENSIONS = ['xlsx', 'csv']
    UPLOAD_PATH = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'data')
    FERNET_KEY = 'juzm4Q6T9ao-ElocILKAAVFQZy6vDz1hcYruKDHL-nQ='
    GOOGLE_CREDENTIALS_PATH = os.path.join(os.path.dirname(
        os.path.realpath(__file__)), 'token.json')
    GOOGLE_FOLDER_ID = '1IlkjFPfkyLHa98aEuIxTvi3Nv3gejj9Z'


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
