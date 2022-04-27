from pymarc import MARCReader
from app.models import *
from app import db
from chardet import detect

class DataProcessor():

    def process_data(self, input_data, source_database):
        if source_database == 0:
            self._process_data_lan(input_data)
        elif source_database == 1:
            self._process_data_rucont(input_data)
        else:
            self._process_data_urait(input_data) 

    # Get file encoding type
    def _get_encoding_type(self, file):
        with open(file, 'rb') as f:
            rawdata = f.read()
        return detect(rawdata)['encoding']

    def insert_source_databases(self):
        source_dbs = []
        for i in range(3):
            source_dbs.append(Database())
        source_dbs[0].name = 'ЭБС Лань'
        source_dbs[1].name = 'ЭБС РУКОНТ'
        source_dbs[2].name = 'ЭБС ЮРАЙТ'
        for i in range(len(source_dbs)):
            db.session.add(source_dbs[i])
        db.session.commit()
            
    def _process_data_lan(self, input_data):
        file_encoding = self._get_encoding_type(input_data)
        # It is assumed that source databases names are already in the database 
        source_database = db.session.query(Database).filter_by(name='ЭБС Лань').scalar()
        with open(input_data, 'rb') as fh:
            reader = MARCReader(fh,  file_encoding=file_encoding)
            for record in reader:
                record_table = Record()
                record_table.database.append(source_database)
                doctype = Doctype()
                publisher = Publisher()
                
                # Title
                if record['200'] is not None: 
                    if record['200']['a'] is not None:
                        record_table.title = str(record['200']['a'])
                    # Doctype
                    if record['200']['b'] is not None:
                        doctype = db.session.query(Doctype).filter_by(name=str(record['200']['b'])).scalar()
                        if doctype is not None:
                            db.session.add(doctype)
                            record_table.doctypes.append(doctype)
                        else:
                            doctype = Doctype(name=str(record['200']['b']))
                            record_table.doctypes.append(doctype)
                            db.session.add(doctype)
                
                # Publishing year
                if record['210'] is not None:
                    if record['210']['d'] is not None:
                        record_table.publishing_year = int(record['210']['d'])
                
                # Description
                if record['330'] is not None:
                    if record['330']['a'] is not None:
                        record_table.description = str(record['330']['a'])
                
                # Cover
                if record['953'] is not None:
                    if record['953']['a'] is not None:
                        record_table.cover = str(record['953']['a'])
                
                # ISBN
                if record['010'] is not None:
                    if record['010']['a'] is not None:
                        record_table.isbn = str(record['010']['a'])
                
                # ISSN
                if record['011'] is not None:
                    if record['011']['a'] is not None:
                        record_table.issn = str(record['011']['a'])
                
                # Pages
                if record['215'] is not None:
                    if record['215']['a'] is not None:
                        record_table.pages = str(record['215']['a'])
                
                # URL
                if record['856'] is not None:
                    if record['856']['u'] is not None:
                        record_table.url = str(record['856']['u'])
                
                # УДК
                if record['675'] is not None: 
                    if record['675']['a'] is not None:
                        record_table.udc = str(record['675']['a'])
                
                # ББК
                if record['686'] is not None: 
                    if record['686']['a'] is not None:
                        record_table.bbk = str(record['686']['a'])
            
                # Authors
                if record['700'] is not None:
                    if record['700']['a'] is not None:
                        if record['700']['b'] is not None:
                            author_name = db.session.query(Author).filter_by(name=str(record['700']['a']) + ' ' + str(record['700']['b'])).scalar()
                            if author_name is not None:
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                            else:
                                author_name = Author(name=str(record['700']['a']) + ' ' + str(record['700']['b']))
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                if record['701'] is not None:
                    if record['701']['a'] is not None and record['701']['b'] is not None:
                        temp = list()
                        for f in record.get_fields('701'):
                            temp.append(str(f['a']) + ' ' + str(f['b']))
                        for val in temp:
                            author_name = db.session.query(Author).filter_by(name=val).scalar()
                            if author_name is not None:
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                            else:
                                author_name = Author(name=val)
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                
                # Publisher
                if record['210'] is not None:
                    if record['210']['c'] is not None:
                        publisher = db.session.query(Publisher).filter_by(name=str(record['210']['c'])).scalar()
                        if publisher is not None:
                            db.session.add(publisher)
                            record_table.publisher.append(publisher)
                        else:
                            publisher = Publisher(name=str(record['210']['c']))
                            record_table.publisher.append(publisher)
                            db.session.add(publisher)
                    
                # TODO: generate bibliographic description
                record_table.bibliographic_description = None
                db.session.add(record_table)
                db.session.commit()
                
    def _process_data_rucont(self, input_data):
        file_encoding = self._get_encoding_type(input_data)
        # It is assumed that source databases names are already in the database 
        source_database = db.session.query(Database).filter_by(name='ЭБС РУКОНТ').scalar()
        with open(input_data, 'rb') as fh:
            reader = MARCReader(fh,  file_encoding=file_encoding)
            for record in reader:
                record_table = Record()
                record_table.database.append(source_database)
                publisher = Publisher()
                
                # Title
                if record['200'] is not None: 
                    if record['200']['a'] is not None:
                        record_table.title = str(record['200']['a'])
                        
                # Doctypes
                if record['203'] is not None:
                    if record['203']['a'] is not None:
                        temp = list()
                        for f in record.get_fields('203'):
                            temp.append(str(f['a']).capitalize())
                        for val in temp:
                            doctype_name = db.session.query(Doctype).filter_by(name=val).scalar()
                            if doctype_name is not None:
                                db.session.add(doctype_name)
                                record_table.doctypes.append(doctype_name)
                            else:
                                doctype_name = Doctype(name=val)
                                record_table.doctypes.append(doctype_name)
                                db.session.add(doctype_name)
                    if record['203']['c'] is not None:
                        temp = list()
                        for f in record.get_fields('203'):
                            temp.append(str(f['c']).capitalize())
                        for val in temp:
                            doctype_name = db.session.query(Doctype).filter_by(name=val).scalar()
                            if doctype_name is not None:
                                db.session.add(doctype_name)
                                record_table.doctypes.append(doctype_name)
                            else:
                                doctype_name = Doctype(name=val)
                                record_table.doctypes.append(doctype_name)
                                db.session.add(doctype_name)
                        
                
                # Publishing year
                if record['210'] is not None:
                    if record['210']['d'] is not None:
                        record_table.publishing_year = int(record['210']['d'])
                
                # Description
                if record['330'] is not None:
                    if record['330']['a'] is not None:
                        record_table.description = str(record['330']['a'])
                
                # Cover
                if record['956'] is not None:
                    if record['956']['a'] is not None:
                        record_table.cover = str(record['956']['a'])
                
                # ISBN
                if record['010'] is not None:
                    if record['010']['a'] is not None:
                        record_table.isbn = str(record['010']['a'])
                
                # ISSN
                if record['011'] is not None:
                    if record['011']['a'] is not None:
                        record_table.issn = str(record['011']['a'])
                
                # Pages
                if record['215'] is not None:
                    if record['215']['a'] is not None:
                        record_table.pages = str(record['215']['a'])
                
                # URL
                if record['856'] is not None:
                    if record['856']['u'] is not None:
                        record_table.url = str(record['856']['u'])
                
                # УДК
                if record['675'] is not None: 
                    if record['675']['a'] is not None:
                        record_table.udc = str(record['675']['a'])
                
                # ББК
                if record['686'] is not None: 
                    if record['686']['a'] is not None:
                        record_table.bbk = str(record['686']['a'])
                
                # Authors
                if record['700'] is not None:
                    if record['700']['a'] is not None and record['700']['b'] is not None:
                        author_name = db.session.query(Author).filter_by(name=str(record['700']['a']) + ' ' + str(record['700']['b'])).scalar()
                        if author_name is not None:
                            record_table.authors.append(author_name)
                            db.session.add(author_name)
                        else:
                            author_name = Author(name=str(record['700']['a']) + ' ' + str(record['700']['b']))
                            record_table.authors.append(author_name)
                            db.session.add(author_name)
                    elif record['700']['a'] is not None and record['700']['g'] is not None:
                        author_name = db.session.query(Author).filter_by(name=str(record['700']['a']) + ' ' + str(record['700']['g'])).scalar()
                        if author_name is not None:
                            record_table.authors.append(author_name)
                            db.session.add(author_name) 
                        else:
                            author_name = Author(name=str(record['700']['a']) + ' ' + str(record['700']['g']))
                            record_table.authors.append(author_name)
                            db.session.add(author_name)
                if record['701'] is not None:
                    if record['701']['a'] is not None and record['701']['b'] is not None:
                        temp = list()
                        for f in record.get_fields('701'):
                            temp.append(str(f['a']) + ' ' + str(f['b']))
                        for val in temp:
                            author_name = db.session.query(Author).filter_by(name=val).scalar()
                            if author_name is not None:
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                            else:
                                author_name = Author(name=val)
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                    elif record['701']['a'] is not None and record['701']['g'] is not None:
                        temp = list()
                        for f in record.get_fields('701'):
                            temp.append(str(f['a']) + ' ' + str(f['g']))
                        for val in temp:
                            author_name = db.session.query(Author).filter_by(name=val).scalar()
                            if author_name is not None:
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                            else:
                                author_name = Author(name=val)
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                if record['702'] is not None:
                    if record['702']['a'] is not None and record['702']['b'] is not None:
                        temp = list()
                        for f in record.get_fields('702'):
                            temp.append(str(f['a']) + ' ' + str(f['b']))
                        for val in temp:
                            author_name = db.session.query(Author).filter_by(name=val).scalar()
                            if author_name is not None:
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                            else:
                                author_name = Author(name=val)
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                    elif record['702']['a'] is not None and record['702']['g'] is not None:
                        temp = list()
                        for f in record.get_fields('702'):
                            temp.append(str(f['a']) + ' ' + str(f['g']))
                        for val in temp:
                            author_name = db.session.query(Author).filter_by(name=val).scalar()
                            if author_name is not None:
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                            else:
                                author_name = Author(name=val)
                                record_table.authors.append(author_name)
                                db.session.add(author_name)
                            
                # Publisher
                if record['210'] is not None:
                    if record['210']['c'] is not None:
                        publisher = db.session.query(Publisher).filter_by(name=str(record['210']['c'])).scalar()
                        if publisher is not None:
                            db.session.add(publisher)
                            record_table.publisher.append(publisher)
                        else:
                            publisher = Publisher(name=str(record['210']['c']))
                            record_table.publisher.append(publisher)
                            db.session.add(publisher)
                    
                # TODO: generate bibliographic description
                record_table.bibliographic_description = None
                db.session.add(record_table)
                db.session.commit()