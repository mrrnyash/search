from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# Authentication
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# User table
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    user_role_id = db.Column(db.Integer, db.ForeignKey('user_role.id', onupdate="CASCADE", ondelete="RESTRICT"))
    role = db.relationship('UserRole', back_populates='users')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
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

# Data storage
# Association table for Many to many relationship
record_author_assoc_table = db.Table('records_authors', db.metadata,
    db.Column('author_id', db.Integer, db.ForeignKey('author.id', onupdate="CASCADE", ondelete="RESTRICT"), primary_key=True),
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
    pages = db.Column(db.Integer)
    url = db.Column(db.String(255), unique=True)
    udc = db.Column(db.String(255), index=True)
    bbk = db.Column(db.String(255), index=True)
    # bibliographic_description = db.Column(db.Text)
    
    # Foreign keys
    source_database_id = db.Column(db.Integer, db.ForeignKey('source_database.id', onupdate="CASCADE", ondelete="RESTRICT"))
    publisher_id = db.Column(db.Integer, db.ForeignKey('publisher.id', onupdate="CASCADE", ondelete="RESTRICT"))
    document_type_id = db.Column(db.Integer, db.ForeignKey('document_type.id', onupdate="CASCADE", ondelete="RESTRICT"))

    # Many to many relationship
    authors = db.relationship('Author', secondary=record_author_assoc_table, lazy='subquery',
        back_populates='author_records', uselist=True)

    # Many to one relationships
    source_database = db.relationship('SourceDatabase', back_populates='source_database_records', lazy=True, uselist=True)
    publisher = db.relationship('Publisher', back_populates='publisher_records', lazy=True, uselist=True)
    document_type = db.relationship('DocumentType', back_populates='document_type_records', lazy=True, uselist=True)

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
class SourceDatabase(db.Model):
    __tablename__ = 'source_database'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    source_database_records = db.relationship('Record', back_populates='source_database')
    
    def __repr__(self):
        return '<SourceDatabase {}>'.format(self.name)

# Child table
class DocumentType(db.Model):
    __tablename__ = 'document_type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    document_type_records = db.relationship('Record',  back_populates='document_type', lazy=True)

    def __repr__(self):
        return '<DocumentType {}>'.format(self.name)

# Child table
class Publisher(db.Model):
    __tablename__ = 'publisher'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), index=True, unique=True, nullable=False)
    publisher_records = db.relationship('Record', back_populates='publisher', lazy=True)

    def __repr__(self):
        return '<Publisher {}>'.format(self.name)
