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
    user_role_id = db.Column(db.Integer, db.ForeignKey('user_role.id', onupdate="CASCADE", ondelete="RESTRICT"))
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
record_author_assoc_table = db.Table('records_authors', db.metadata,
    db.Column('author_id', db.Integer, db.ForeignKey('author.id', onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True),
    db.Column('record_id', db.Integer, db.ForeignKey('record.id', onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True)
)

record_doctype_assoc_table = db.Table('records_doctypes', db.metadata,
    db.Column('doctype_id', db.Integer, db.ForeignKey('doctype.id', onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True),
    db.Column('record_id', db.Integer, db.ForeignKey('record.id', onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True)
)

# Parent table
class Record(db.Model):
    __tablename__ = 'record'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    publishing_year = db.Column(db.SmallInteger())
    description = db.Column(db.Text)
    cover = db.Column(db.String(255), unique=True)
    isbn = db.Column(db.String(255), index=True)
    issn = db.Column(db.String(255), index=True)
    pages = db.Column(db.String(20))
    url = db.Column(db.String(255), unique=True)
    udc = db.Column(db.String(255), index=True)
    bbk = db.Column(db.String(255), index=True)
    bibliographic_description = db.Column(db.Text)
    database_id = db.Column(db.Integer, db.ForeignKey('database.id', onupdate="CASCADE", ondelete="RESTRICT"))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id', onupdate="CASCADE", ondelete="RESTRICT"))

    # Many to many relationships
    authors = db.relationship('Author', secondary=record_author_assoc_table, lazy='subquery',
        back_populates='author_records', uselist=True)
    doctypes = db.relationship('Doctype', secondary=record_doctype_assoc_table, lazy='subquery',
        back_populates='doctype_records', uselist=True)

    # Many to one relationships
    database = db.relationship('Database', back_populates='database_records', lazy=True, uselist=True)
    publisher = db.relationship('Publisher', back_populates='publisher_records', lazy=True, uselist=True)

# Method of printing object of the class
    def __repr__(self):
        return '<Record {}>'.format(self.bibliographic_description)

# Child table
class Author(db.Model):
    __tablename__ = 'author'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, nullable=False, unique=True)
    author_records = db.relationship('Record', secondary=record_author_assoc_table,  
            back_populates='authors', lazy='subquery', uselist=True)
    
    def __repr__(self):
        return '<Author {}>'.format(self.name)

# Child table
class Database(db.Model):
    __tablename__ = 'database'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    database_records = db.relationship('Record', back_populates='database')
    
    def __repr__(self):
        return '<Database {}>'.format(self.name)

# Child table
class Doctype(db.Model):
    __tablename__ = 'doctype'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    doctype_records = db.relationship('Record', secondary=record_doctype_assoc_table,  
            back_populates='doctypes', lazy='subquery', uselist=True)

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
