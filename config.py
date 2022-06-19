import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config(object):
    ROOT_DIR = os.environ.get('ROOT_DIR')
    SECRET_KEY = os.environ.get('SECRET KEY') or 'you-will-never-guess'

    # MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/search'

    # disable the feature of signaling the application every time 
    # a change is about to be made in the database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Sending Errors by Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['exampleh@example.com']

    RECORDS_PER_PAGE = 10

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

    UPLOAD_FOLDER = os.path.join(basedir, os.environ.get('UPLOAD_FOLDER'))
    REPORT_FOLDER = os.path.join(basedir, os.environ.get('REPORT_FOLDER'))
    ALLOWED_EXTENSIONS = os.environ.get('ALLOWED_EXTENSIONS')
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024






