from pymarc import MARCReader

class DataProcessor():

    def process_marc(self, input_data):
        fetched_data = {dict.fromkeys(['title',
                                'publishing_year',
                                'description',
                                'cover',
                                'isbn_issn',
                                'num_pages',
                                'url',
                                'udk',
                                'bbk',
                                'bibliographic_description',
                                'database_id',
                                'document_type_id',
                                'publisher_id'])}

        with open(input_data, 'rb'):
                  reader = MARCReader(input_data, to_unicode=True, force_utf8=True)
                  for record in reader:
                      fetched_data['title'] = str(record['200']['a'])
                      fetched_data['publishing_year'] = int(record['210']['d'])
                      fetched_data['description'] = str(record['330']['a'])
                      fetched_data['cover'] = str(record['953']['a'])
                      fetched_data['isbn_issn'] = str(record['010']['a'])
                      fetched_data['num_pages'] = str(record['215']['a'])
                      fetched_data['url'] = str(record['856']['u'])
                      fetched_data['udk'] = str(record['675']['a'])
                      fetched_data['bbk'] = str(record['686']['a'])
                      fetched_data['bibliographic_description'] = ''
                      fetched_data['database_id'] = int(1)
                      fetched_data['document_type_id'] = int(1)
                      fetched_data['publisher_id'] = int(1)
        
        for key in fetched_data:
            print(fetched_data[key])
                      





