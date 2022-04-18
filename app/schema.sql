DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS user_role;
DROP TABLE IF EXISTS author;
DROP TABLE IF EXISTS record_author;
DROP TABLE IF EXISTS record;
DROP TABLE IF EXISTS db;
DROP TABLE IF EXISTS doctype;
DROP TABLE IF EXISTS publisher;

CREATE TABLE user_role (
    role_id INT(3) NOT NULL AUTO_INCREMENT,
    role_name VARCHAR(100) NOT NULL,
    PRIMARY KEY(role_id)
    ) ENGINE=INNODB;

CREATE TABLE user (
    user_id INT(11) NOT NULL AUTO_INCREMENT,
    user_role INT(3),
    user_login VARCHAR(100) NOT NULL,
    user_email VARCHAR(100) NOT NULL,
    user_password CHAR(60) NOT NULL,
    user_salt CHAR(29) NOT NULL,
    PRIMARY KEY(user_id),
    FOREIGN KEY(user_role),
        REFERENCES user_role(role_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=INNODB;

CREATE TABLE publisher (
    publisher_id INT(11) NOT NULL AUTO_INCREMENT,
    publisher_name VARCHAR(255) NOT NULL,
    PRIMARY KEY(publisher_id)
) ENGINE=INNODB;

CREATE TABLE doctype (
    doctype_id INT(11) NOT NULL AUTO_INCREMENT,
    doctype_name VARCHAR(255) NOT NULL,
    PRIMARY KEY(doctype_id)
) ENGINE=INNODB;

CREATE TABLE db (
    db_id INT(11) NOT NULL AUTO_INCREMENT,
    db_name VARCHAR(100) NOT NULL,
    PRIMARY KEY(db_id)
) ENGINE=INNODB;

CREATE TABLE author (
    author_id INT(11) NOT NULL AUTO_INCREMENT,
    author_name VARCHAR(100) NOT NULL,
    PRIMARY KEY(author_id)
) ENGINE=INNODB;

CREATE TABLE record (
    record_id INT(11) NOT NULL AUTO_INCREMENT,
    db INT(11),
    document_type INT(11),
    publisher INT(11),
    cover VARCHAR(255),
    title VARCHAR(255) NOT NULL,
    publishing_year SMALLINT UNSIGNED,
    isbn_issn VARCHAR(17),
    num_pages SMALLINT UNSIGNED,
    doc_url VARCHAR(255),
    udc VARCHAR(255),
    bbk VARCHAR(255),
    doc_description TEXT,
    bibliographic_desc TEXT,
    PRIMARY KEY(record_id),
    FOREIGN KEY(db) 
        REFERENCES db(db_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY(document_type)
        REFERENCES doctype(doctype_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY(publisher)
        REFERENCES publisher(publisher_id)
        ON UPDATE CASCADE ON DELETE RESTRICT 
) ENGINE=INNODB;

CREATE TABLE record_author (
    record_author_id INT(11) NOT NULL AUTO_INCREMENT,
    record_id INT(11),
    author_id INT(11),
    PRIMARY KEY(record_author_id),
    FOREIGN KEY(record_id)
        REFERENCES record(record_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    FOREIGN KEY(author_id)
        REFERENCES author(author_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=INNODB;