import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET KEY') or 'you-will-never-guess'
    
    # the location of the application's database 
    # SQLite
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    #     'sqlite:///' + os.path.join(basedir, 'app.db')

    # MySQL
    SQLALCHEMY_DATABASE_URI = 'mysql://root:@localhost/searchbsu' 
    
    # disable the feature of signaling the application every time 
    # a change is about to be made in the database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
