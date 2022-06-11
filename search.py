from app import create_app, db
from app.models import User, UserRole, Record, Author, \
    SourceDatabase, DocumentType, Publisher, Keyword

app = create_app()


# Create a shell context for testing in Python interpreter
@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'User': User,
            'UserRole': UserRole,
            'Record': Record,
            'Author': Author,
            'SourceDatabase': SourceDatabase,
            'DocumentType': DocumentType,
            'Publisher': Publisher,
            'Keyword': Keyword}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
