from sqlalchemy import ForeignKey
from app import db

class UserRole(db.Model):
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return '<UserRole {}>'.format(self.role_name)

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    user_role = db.Column(db.Integer, db.ForeignKey('user_role.role_id'))
    user_email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

class Author(db.Model):
    author_id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), index=True)

    def __repr__(self):
        return '<Author {}>'.format(self.author_name)
    

class RecordAuthor(db.Model):
    record_author_id = db.Column(db.Integer, primary_key=True)
    record_id = db.Column(db.Integer, db.ForeignKey('record.record_id'))
    author_id = db.Column(db.Integer, db.ForeignKey('author.author_id'))

class Extdb(db.Model):
    extdb_id = db.Column(db.Integer, primary_key=True)
    extdb_name = db.Column(db.String(100), index=True)

    def __repr__(self):
        return '<Extdb {}>'.format(self.extdb_name)

class Doctype(db.Model):
    doctype_id = db.Column(db.Integer, primary_key=True)
    doctype_name = db.Column(db.String(100), index=True, unique=True)

    def __repr__(self):
        return '<Doctype {}>'.format(self.doctype_name)

class Publisher(db.Model):
    publisher_id = db.Column(db.Integer, primary_key=True)
    publisher_name = db.Column(db.String(255), index=True, unique=True)

    def __repr__(self):
        return '<Publisher {}>'.format(self.publisher_name)

class Record(db.Model):
    record_id = db.Column(db.Integer, primary_key=True)
    extdb = db.Column(db.Integer, db.ForeignKey('extdb.extdb_id'))
    document_type = db.Column(db.Integer, db.ForeignKey('doctype.doctype_id'))
    publisher = db.Column(db.Integer, db.ForeignKey('publisher.publisher_id'))
    cover = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(255))
    publishing_year = db.Column(db.SmallInteger())
    isbn_issn = db.Column(db.String(17), index=True, unique=True)
    num_pages = db.Column(db.SmallInteger)
    url = db.Column(db.String(255), unique=True)
    udk = db.Column(db.String(255), index=True, unique=True)
    bbk = db.Column(db.String(255), index=True, unique=True)
    description = db.Column(db.Text)
    biblio = db.Column(db.Text)
