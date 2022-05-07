import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET KEY') or 'd73216725c044f0487d9534ae9bf4c21'

    # the location of the application's database 
    # SQLite
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')

    # MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/searchlib'

    # disable the feature of signaling the application every time 
    # a change is about to be made in the database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Sending Errors by Email
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['mrrnyash@gmail.com']

    RECORDS_PER_PAGE = 10

    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')

