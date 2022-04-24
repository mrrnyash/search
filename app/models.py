from sqlalchemy import ForeignKey
from app import db

# Authentication
# Parent table
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('user_role.id'))
    role = db.relationship('UserRole', back_populates='users')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

# Child table
class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    # One to many relationship
    users = db.relationship('User', back_populates='role', lazy=True)
    
    def __repr__(self):
        return '<UserRole {}>'.format(self.name)


# Association table for Many to many relationship
records_authors = db.Table('records_authors', db.metadata,
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'), primary_key=True),
    db.Column('record_id', db.Integer, db.ForeignKey('record.id'), primary_key=True)
)

# Parent table
class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    publishing_year = db.Column(db.SmallInteger())
    description = db.Column(db.Text)
    cover = db.Column(db.String(255), unique=True)
    isbn_issn = db.Column(db.String(17), index=True, unique=True)
    pages = db.Column(db.SmallInteger)
    url = db.Column(db.String(255), unique=True)
    udk = db.Column(db.String(255), index=True, unique=True)
    bbk = db.Column(db.String(255), index=True, unique=True)
    bibliographic_description = db.Column(db.Text)
    database_id = db.Column(db.Integer, db.ForeignKey('database.id'),
                nullable=False)
    doctype_id = db.Column(db.Integer, db.ForeignKey('doctype.id'))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id'))

    # Many to many relationship
    authors = db.relationship('Author', secondary=records_authors, lazy='subquery',
        back_populates='author_records', uselist=True)

    # Many to one relationships
    database = db.relationship('Database', back_populates='database_records', lazy=True, uselist=True)
    doctype = db.relationship('Doctype', back_populates='doctype_records', lazy=True, uselist=True)
    publisher = db.relationship('Publisher', back_populates='publisher_records', lazy=True, uselist=True)

# Method of printing object of the class
    def __repr__(self):
        return '<Record {}>'.format(self.bibliographic_description)

# Child table
class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, nullable=False)
    author_records = db.relationship('Record', secondary=records_authors,  
            back_populates='authors', lazy='subquery')
    
    def __repr__(self):
        return '<Author {}>'.format(self.name)

# Child table
class Database(db.Model):
    __tablename__ = 'database'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, nullable=False)
    database_records = db.relationship('Record', back_populates='database')
    
    def __repr__(self):
        return '<Database {}>'.format(self.name)

# Child table
class Doctype(db.Model):
    __tablename__ = 'doctype'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    doctype_records = db.relationship('Record', back_populates='doctype', lazy=True)

    def __repr__(self):
        return '<Doctype {}>'.format(self.name)

# Child table
class Publisher(db.Model):
    __tablename__ = 'publisher'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True, nullable=False)
    publisher_records = db.relationship('Record', back_populates='publisher', lazy=True)

    def __repr__(self):
        return '<Publisher {}>'.format(self.name)
