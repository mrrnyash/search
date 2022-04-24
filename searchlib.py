from app import app, db
from app.models import *

# Create a shell context for testing in Python interpreter
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 
    'User': User, 
    'UserRole': UserRole,
    'Record': Record,
    'Author': Author,
    'Database': Database,
    'Doctype': Doctype,
    'Publisher': Publisher}