from pymarc import MARCReader
from app import db
from app.models import *
from chardet import detect
import re

DOCUMENT_TYPES = {
    'a': 'Статьи, периодика',
    'b': 'Часть сериального ресурса',
    'c': 'Собрание (коллекция, подборка)',
    'd': 'Часть собрания (коллекции, подборки)',
    'i': 'Интегрируемый ресурс',
    'm': 'Монография',
    's': 'Сериальный ресурс'
    }

class MARCProcessor():
    
    # Get file encoding type
    # ! This is very inefficient for big data
    def _get_encoding_type(self, file):
        with open(file, 'rb') as f:
            rawdata = f.read()
        return detect(rawdata)['encoding']
    
    def process_rusmarc(self, input_data):
        # Get file encoding
        file_encoding = self._get_encoding_type(input_data)
        # Get source database once
        with open(input_data, 'rb') as fh:
            reader = MARCReader(fh,  file_encoding=file_encoding)
            for record in reader:
                if record['801'] is not None:
                    if record['801']['b'] is not None:
                        source_database_name = record['801']['b']
                        break
                        
        source_database_entry = db.session.query(SourceDatabase).filter_by(name=source_database_name).scalar()
        if source_database_entry is None:
            source_database_entry = SourceDatabase(name=source_database_name)
            
        with open(input_data, 'rb') as fh:
            reader = MARCReader(fh,  file_encoding=file_encoding)
            for record in reader:
                record_table = Record()
                record_table.source_database.append(source_database_entry)
                db.session.add(source_database_entry)
                
                # Title
                if record['200'] is not None: 
                    if record['200']['a'] is not None:
                        record_table.title = record['200']['a']
                        
                # Document type
                document_type_entry = db.session.query(DocumentType).filter_by(name=DOCUMENT_TYPES.get(record.leader[7])).scalar()
                if document_type_entry is not None:
                    db.session.add(document_type_entry)
                    record_table.document_type.append(document_type_entry)
                else:
                    document_type_entry = DocumentType(name=DOCUMENT_TYPES.get(record.leader[7]))
                    record_table.document_type.append(document_type_entry)
                    db.session.add(document_type_entry)
                
                # Publishing year
                if record['210'] is not None:
                    if record['210']['d'] is not None:
                        record_table.publishing_year = int(record['210']['d'])
                
                # Description
                if record['330'] is not None:
                    if record['330']['a'] is not None:
                        record_table.description = record['330']['a']
                
                # Cover                            
                if record['953'] is not None:
                    if record['953']['a'] is not None:
                        record_table.cover = record['953']['a']
                elif record['956'] is not None:
                    if record['956']['a'] is not None:
                        record_table.cover = record['956']['a']
                
                # ISBN
                if record['010'] is not None:
                    if record['010']['a'] is not None:
                        record_table.isbn = record['010']['a']
                
                # ISSN
                if record['011'] is not None:
                    if record['011']['a'] is not None:
                        record_table.issn = record['011']['a']
                
                # Pages
                if record['215'] is not None:
                    if record['215']['a'] is not None:
                        temp = re.findall(r'\d+', str(record['215']['a']))
                        record_table.pages = int(temp[0])
                
                # URL
                if record['856'] is not None:
                    if record['856']['u'] is not None:
                        record_table.url = record['856']['u']
                
                # udc
                if record['675'] is not None: 
                    if record['675']['a'] is not None:
                        record_table.udc = str(record['675']['a'])
                
                # bbk
                if record['686'] is not None: 
                    if record['686']['a'] is not None:
                        record_table.bbk = str(record['686']['a'])
            
                # Authors
                if record['700'] is not None:
                    if record['700']['a'] is not None:
                        if record['700']['b'] is not None:
                            author_entry = db.session.query(Author).filter_by(name=record['700']['a'] + ' ' + record['700']['b']).scalar()
                            if author_entry is not None:
                                record_table.authors.append(author_entry)
                                db.session.add(author_entry)
                            else:
                                author_entry = Author(name=record['700']['a'] + ' ' + record['700']['b'])
                                record_table.authors.append(author_entry)
                                db.session.add(author_entry)
                        elif record['700']['g'] is not None:
                            initials = record['700']['g'].split()
                            for i in range(len(initials)):
                                initials[i] = initials[i][0] + '.'
                            initials = ' '.join([str(item) for item in initials])
                            author_entry = db.session.query(Author).filter_by(name=record['700']['a'] + ' ' + initials).scalar()
                            if author_entry is not None:
                                record_table.authors.append(author_entry)
                                db.session.add(author_entry)
                            else:
                                author_entry = Author(name=record['700']['a'] + ' ' + initials)
                                record_table.authors.append(author_entry)
                                db.session.add(author_entry)
                if record['701'] is not None:
                    if record['701']['a'] is not None:
                        if record['701']['b'] is not None:
                            authors_list = []
                            for f in record.get_fields('701'):
                                if f['a'] is not None and f['b'] is not None:
                                    authors_list.append(f['a'] + ' ' + f['b'])
                            for val in authors_list:
                                author_entry = db.session.query(Author).filter_by(name=val).scalar()
                                if author_entry is not None:
                                    record_table.authors.append(author_entry)
                                    db.session.add(author_entry)
                                else:
                                    author_entry = Author(name=val)
                                    record_table.authors.append(author_entry)
                                    db.session.add(author_entry)
                        elif record['701']['a'] is not None:
                            if record['701']['g'] is not None:
                                authors_list = []
                                for f in record.get_fields('701'):
                                    if f['a'] is not None and f['g'] is not None:
                                        initials = f['g'].split()
                                        for i in range(len(initials)):
                                            initials[i] = initials[i][0] + '.'
                                        initials = ' '.join([str(item) for item in initials])
                                        authors_list.append(f['a'] + ' ' + initials)
                                for val in authors_list:
                                    author_entry = db.session.query(Author).filter_by(name=val).scalar()
                                    if author_entry is not None:
                                        record_table.authors.append(author_entry)
                                        db.session.add(author_entry)
                                    else:
                                        author_entry = Author(name=val)
                                        record_table.authors.append(author_entry)
                                        db.session.add(author_entry)
                if record['702'] is not None:
                    if record['702']['a'] is not None and record['702']['b'] is not None:
                        authors_list = []
                        for f in record.get_fields('702'):
                            if f['a'] is not None and f['b'] is not None:
                                authors_list.append(f['a'] + ' ' + f['b'])
                        for val in authors_list:
                            author_entry = db.session.query(Author).filter_by(name=val).scalar()
                            if author_entry is not None:
                                record_table.authors.append(author_entry)
                                db.session.add(author_entry)
                            else:
                                author_entry = Author(name=val)
                                record_table.authors.append(author_entry)
                                db.session.add(author_entry)
                    elif record['702']['a'] is not None:
                        if record['702']['g'] is not None:
                            authors_list = []
                            for f in record.get_fields('702'):
                                if f['a'] is not None and f['g'] is not None:
                                    initials = f['g'].split()
                                for i in range(len(initials)):
                                    initials[i] = initials[i][0] + '.'
                                initials = ' '.join([str(item) for item in initials])
                                authors_list.append(f['a'] + ' ' + initials)
                            for val in authors_list:
                                author_entry = db.session.query(Author).filter_by(name=val).scalar()
                                if author_entry is not None:
                                    record_table.authors.append(author_entry)
                                    db.session.add(author_entry)
                                else:
                                    author_entry = Author(name=val)
                                    record_table.authors.append(author_entry)
                                    db.session.add(author_entry)
                                
                # Publisher
                if record['210'] is not None:
                    if record['210']['c'] is not None:
                        publisher_entry = db.session.query(Publisher).filter_by(name=record['210']['c']).scalar()
                        if publisher_entry is not None:
                            db.session.add(publisher_entry)
                            record_table.publisher.append(publisher_entry)
                        else:
                            publisher_entry = Publisher(name=record['210']['c'])
                            record_table.publisher.append(publisher_entry)
                            db.session.add(publisher_entry)
                            
                # TODO: generate bibliographic description
                # record_table.bibliographic_description = None
                db.session.add(record_table)
                db.session.commit()
                
    def process_marc21(self, input_data):
        file_encoding = 'cp1251'
        # file_encoding = self._get_encoding_type(input_data)
        with open(input_data, 'rb') as fh:
            reader = MARCReader(fh,  file_encoding=file_encoding)
            for record in reader:
                if record['040'] is not None:
                    if record['040']['a'] is not None:
                        source_database_name = record['040']['a']
                        break
            
        source_database_entry = db.session.query(SourceDatabase).filter_by(name=source_database_name).scalar()               
        if source_database_entry is None:
            source_database_entry = SourceDatabase(name=source_database_name)
            
        with open(input_data, 'rb') as fh:
            reader = MARCReader(fh,  file_encoding=file_encoding)
            for record in reader:
                record_table = Record()
                record_table.source_database.append(source_database_entry)
                
                # Title
                if record.title() is not None: 
                    record_table.title = record.title()
                        
                # Document type
                document_type_entry = db.session.query(DocumentType).filter_by(name=DOCUMENT_TYPES.get(record.leader[7])).scalar()
                if document_type_entry is not None:
                    db.session.add(document_type_entry)
                    record_table.document_type.append(document_type_entry)
                else:
                    document_type_entry = DocumentType(name=DOCUMENT_TYPES.get(record.leader[7]))
                    record_table.document_type.append(document_type_entry)
                    db.session.add(document_type_entry)                        
                
                # Publishing year
                if record['260'] is not None:
                    if record['260']['c'] is not None:
                        record_table.publishing_year = record['260']['c']
                
                # Description
                if record['520'] is not None:
                    if record['520']['a'] is not None:
                        record_table.description = str(record['520']['a'])
                
                # Cover
                if record['856'] is not None:
                    if record['856']['x'] is not None:
                        record_table.cover = record['856']['x']

                # ISBN
                if record['020'] is not None:
                    if record['020']['a'] is not None:
                        record_table.isbn = record['020']['a']
                
                # ISSN
                if record['022'] is not None:
                    if record['022']['a'] is not None:
                        record_table.issn = record['022']['a']
                
                # Pages
                if record['300'] is not None:
                    if record['300']['a'] is not None:
                        temp = re.findall(r'\d+', str(record['300']['a']))
                        record_table.pages = int(temp[0])
                
                # URL
                if record['856'] is not None:
                    if record['856']['u'] is not None:
                        record_table.url = record['856']['u']
                elif record['003'] is not None:
                    record_table.url = record['003']
                
                # УДК
                if record['080'] is not None: 
                    if record['080']['a'] is not None:
                        record_table.udc = str(record['080']['a'])
                
                # ББК
                if record['084'] is not None: 
                    if record['084']['a'] is not None:
                        record_table.bbk = record['084']['a']
                        
                # Authors
                if record['100'] is not None:
                    if record['100']['a'] is not None:
                        author_entry = db.session.query(Author).filter_by(name=record['100']['a']).scalar()
                        if author_entry is not None:
                            record_table.authors.append(author_entry)
                            db.session.add(author_entry)
                        else:
                            author_entry = Author(name=record['100']['a'])
                            record_table.authors.append(author_entry)
                            db.session.add(author_entry)
                if record['700'] is not None:
                    if record['700']['a'] is not None:
                        authors_list = []
                        for f in record.get_fields('700'):
                            authors_list.append(f['a'])
                        for val in authors_list:
                            author_entry = db.session.query(Author).filter_by(name=val).scalar()
                            if author_entry is not None:
                                record_table.authors.append(author_entry)
                                db.session.add(author_entry)
                            else:
                                author_entry = Author(name=val)
                                record_table.authors.append(author_entry)
                                db.session.add(author_entry)
                            
                # Publisher
                if record['260'] is not None:
                    if record['260']['b'] is not None:
                        publisher_entry = db.session.query(Publisher).filter_by(name=record.publisher()).scalar()
                        if publisher_entry is not None:
                            db.session.add(publisher_entry)
                            record_table.publisher.append(publisher_entry)
                        else:
                            publisher_entry = Publisher(name=record.publisher())
                            record_table.publisher.append(publisher_entry)
                            db.session.add(publisher_entry)
                    
                # TODO: generate bibliographic description
                # record_table.bibliographic_description = None
                db.session.add(record_table)
                db.session.commit()