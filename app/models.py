from sqlalchemy import ForeignKey
from app import db

# Parent table
class UserRole(db.Model):
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(100), unique=True)
    
    # One to many relationship
    users = db.relationship('User', backref='user_role', lazy=True)
    
    # Method of printing object of the class
    def __repr__(self):
        return '<UserRole {}>'.format(self.role_name)

# Child table
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    user_email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('user_role.role_id'))

    def __repr__(self):
        return '<User {}>'.format(self.username)

# Parent table
class Database(db.Model):
    database_id = db.Column(db.Integer, primary_key=True)
    database_name = db.Column(db.String(100), index=True, nullable=False)
    
    # One to many relationship
    records = db.relationship('Record', backref='database', lazy=True)

    def __repr__(self):
        return '<Database {}>'.format(self.database_name)

# Parent table
class Doctype(db.Model):
    doctype_id = db.Column(db.Integer, primary_key=True)
    doctype_name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    
    # One to many relationship
    records = db.relationship('Record', backref='doctype', lazy=True)

    def __repr__(self):
        return '<Doctype {}>'.format(self.doctype_name)

# Parent table
class Publisher(db.Model):
    publisher_id = db.Column(db.Integer, primary_key=True)
    publisher_name = db.Column(db.String(255), index=True, unique=True, nullable=False)
    
    # One to many relationship
    records = db.relationship('Record', backref='publisher', lazy=True)

    def __repr__(self):
        return '<Publisher {}>'.format(self.publisher_name)

# Association table
author_record = db.Table('author_record', 
    db.Column('author_id', db.Integer, db.ForeignKey('author.author_id')),
    db.Column('record_id', db.Integer, db.ForeignKey('record.record_id'))
)

# Parent table
class Author(db.Model):
    author_id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), index=True, nullable=False)

    # Many to many relationship
    records = db.relationship('Author', secondary=author_record, backref='authors')

    def __repr__(self):
        return '<Author {}>'.format(self.author_name)

# Child table
class Record(db.Model):
    record_id = db.Column(db.Integer, primary_key=True)
    cover = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(255), nullable=False)
    publishing_year = db.Column(db.SmallInteger())
    isbn_issn = db.Column(db.String(17), index=True, unique=True)
    num_pages = db.Column(db.SmallInteger)
    url = db.Column(db.String(255), unique=True)
    udk = db.Column(db.String(255), index=True, unique=True)
    bbk = db.Column(db.String(255), index=True, unique=True)
    description = db.Column(db.Text)
    bibliographic_description = db.Column(db.Text)
    database_id = db.Column(db.Integer, db.ForeignKey('database.database_id'))
    document_type_id = db.Column(db.Integer, db.ForeignKey('doctype.doctype_id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.publisher_id'))

    def __repr__(self):
        return '<Record {}>'.format(self.title)