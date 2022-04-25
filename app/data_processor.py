from pymarc import MARCReader
from app.models import *
from app import db
from chardet import detect



class DataProcessor():

    # Get file encoding type
    def get_encoding_type(self, file):
        with open(file, 'rb') as f:
            rawdata = f.read()
        return detect(rawdata)['encoding']

    def process_data(self, input_data):

        file_encoding = self.get_encoding_type(input_data)

        fetched_data = dict.fromkeys(['title',
                                'publishing_year',
                                'description',
                                'cover',
                                'isbn',
                                'issn',
                                'pages',
                                'url',
                                'udc',
                                'bbk',
                                'bibliographic_description',
                                'authors',
                                'database',
                                'doctype',
                                'publisher'])

        with open(input_data, 'rb') as fh:
                  reader = MARCReader(fh, file_encoding=file_encoding)
                  for record in reader:

                      record_table = Record()
                      doctype = Doctype()
                      publisher = Publisher()
                      database = Database()

                      if record['200'] is not None: 
                          if record['200']['a'] is not None:
                              fetched_data['title'] = str(record['200']['a'])
                              record_table.title=fetched_data['title']
                          if record['200']['b'] is not None:
                              fetched_data['doctype'] = str(record['200']['b'])
                              doctype = db.session.query(Doctype).filter_by(name=fetched_data['doctype']).scalar()
                              if doctype is not None:
                                  db.session.add(doctype)
                                  record_table.doctype.append(doctype)
                              else:
                                  doctype = Doctype(name=fetched_data['doctype'])
                                  record_table.doctype.append(doctype)
                                  db.session.add(doctype)

                      if record['210'] is not None and record['210']['d'] is not None:
                          fetched_data['publishing_year'] = int(record['210']['d'])
                          record_table.publishing_year=fetched_data['publishing_year']
                          

                      if record['330'] is not None and record['330']['a'] is not None:
                          fetched_data['description'] = str(record['330']['a'])
                          record_table.description=fetched_data['description']
                            

                      if record['953'] is not None and record['953']['a'] is not None:
                          fetched_data['cover'] = str(record['953']['a'])
                          record_table.cover=fetched_data['cover']
                            

                      if record['010'] is not None and record['010']['a'] is not None:
                          fetched_data['isbn'] = str(record['010']['a'])
                          record_table.isbn=fetched_data['isbn']

                      if record['011'] is not None and record['011']['a'] is not None:
                          fetched_data['issn'] = str(record['011']['a'])
                          record_table.issn=fetched_data['issn']
                            

                      if record['215'] is not None and record['215']['a'] is not None:
                          fetched_data['pages'] = str(record['215']['a'])
                          record_table.pages=fetched_data['pages']
                            

                      if record['856'] is not None and record['856']['u'] is not None:
                          fetched_data['url'] = str(record['856']['u'])
                          record_table.url=fetched_data['url']
                            

                      if record['675'] is not None and record['675']['a'] is not None:
                          fetched_data['udc'] = str(record['675']['a'])
                          record_table.udc=fetched_data['udc']
                            

                      if record['686'] is not None and record['686']['a'] is not None:
                          fetched_data['bbk'] = str(record['686']['a'])
                          record_table.bbk=fetched_data['bbk']
                            

                      if record['700'] is not None:
                          fetched_data['authors'] = str(record['700']['a']) + ' ' + str(record['700']['b'])
                          author_1 = Author(name=fetched_data['authors'])
                          record_table.authors.append(author_1)
                          db.session.add(author_1)
                         
                          if record['701'] is not None:
                              fetched_data['authors'] = str(record['701']['a']) + ' ' + str(record['701']['b'])
                              author_2 = Author(name=fetched_data['authors'])
                              record_table.authors.append(author_2)
                              db.session.add(author_2)
                            
                              if record['702'] is not None:
                                  fetched_data['authors'] = str(record['702']['a']) + ' ' + str(record['702']['b'])
                                  author_3 = Author(name=fetched_data['authors'])
                                  record_table.authors.append(author_3)
                                  db.session.add(author_3)
                                 
                      
                      if record['801'] is not None and record['801']['b'] is not None:
                            fetched_data['database'] = str(record['801']['b'])
                            # Check if the database entry is already exists
                            database = db.session.query(Database).filter_by(name=fetched_data['database']).scalar()
                            if database is not None:
                                db.session.add(database)
                                record_table.database.append(database)
                            else:
                                database = Database(name=fetched_data['database'])
                                record_table.database.append(database)
                                db.session.add(database)

                      if record['210'] is not None and record['210']['c'] is not None:
                            fetched_data['publisher'] = str(record['210']['c'])
                            publisher = db.session.query(Publisher).filter_by(name=fetched_data['publisher']).scalar()
                            if publisher is not None:
                                db.session.add(publisher)
                                record_table.publisher.append(publisher)
                            else:
                                publisher = Publisher(name=fetched_data['publisher'])
                                record_table.publisher.append(publisher)
                                db.session.add(publisher)
                    
                      
                      # TODO: generate bibliographic description
                      fetched_data['bibliographic_description'] = 'Здесь будет библиографическая запись'
                      record_table.bibliographic_description=fetched_data['bibliographic_description']

                      db.session.add(record_table)
                      db.session.commit()
                      fetched_data.clear()