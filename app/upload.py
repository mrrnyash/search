import os
import re

from chardet.universaldetector import UniversalDetector
from pymarc import MARCReader
from pymarc import exceptions as exc
from app.models import Record, Author, Keyword, \
    SourceDatabase, DocumentType, Publisher
from app import db
from flask import current_app
from pathlib import Path
from multiprocessing import Process, cpu_count

DOCUMENT_TYPES = {
    'a': 'Статьи, периодика',
    'b': 'Часть сериального ресурса',
    'c': 'Собрание (коллекция, подборка)',
    'd': 'Часть собрания (коллекции, подборки)',
    'i': 'Интегрируемый ресурс',
    'm': 'Монографический ресурс',
    's': 'Сериальный ресурс'
}

ENCODING_TYPES = ['cp1251', 'utf-8']

HASH_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'hashes.txt'))
file = Path(HASH_FILE)
file.touch(exist_ok=True)

UPLOAD_ERRORS_LOG = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'upload_errors.log'))
file = Path(UPLOAD_ERRORS_LOG)
file.touch(exist_ok=True)

TEMP_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'temp.iso'))


# file = Path(TEMP_FILE)
# file.touch(exist_ok=True)


# Get file encoding type
def get_encoding_type(input_data):
    data = open(input_data, 'rb')
    detector = UniversalDetector()
    for line in data.readlines():
        res = detector.result['encoding']
        detector.feed(line)
        if detector.done:
            break
    detector.close()
    data.close()
    return detector.result['encoding']


def bpow(a, n, mod):
    res = 1
    while n:
        if n & 1:
            res = (res * a) % mod
        a = (a * a) % mod
        n >>= 1
    return res


class DBLoader:
    N = 1000
    p1 = 199
    p2 = 203
    mod1 = 1e18 + 7
    mod2 = 1e18 + 9
    P1 = []
    P2 = []

    @classmethod
    def _probe_encoding_types(cls, input_data):
        file_encoding = None
        for encoding in ENCODING_TYPES:
            with open(input_data, 'rb') as fh:
                reader = MARCReader(fh, file_encoding=encoding)
                for record in reader:
                    if record is None:
                        break
                    else:
                        file_encoding = encoding
                        break
        if file_encoding is None:
            return None
        return file_encoding

    @classmethod
    def _get_metadata(cls, input_data):
        marc_file = os.path.join(current_app.config['UPLOAD_FOLDER'], input_data)
        # Get file encoding
        file_encoding = cls._probe_encoding_types(marc_file)

        if file_encoding is None:
            return None

        # Get source database once
        with open(marc_file, 'rb') as fh:
            reader = MARCReader(fh, file_encoding=file_encoding)
            for record in reader:
                if record['801'] is not None:
                    if record['801']['b'] is not None:
                        source_database_name = record['801']['b']
                        break
                elif record['040'] is not None:
                    if record['040']['a'] is not None:
                        source_database_name = record['040']['a']
                        break
        return source_database_name, file_encoding

    @classmethod
    def _gen_p(cls):
        cls.P1 = []
        cls.P2 = []
        for i in range(0, cls.N, 1):
            cls.P1.append(bpow(cls.p1, i, cls.mod1))
        for i in range(0, cls.N, 1):
            cls.P2.append(bpow(cls.p2, i, cls.mod2))

    @classmethod
    def _hash(cls, s):
        s_hash_1 = 0
        s_hash_2 = 0
        if len(cls.P1) == 0:
            cls._gen_p()

        for i in range(0, len(s), 1):
            s_hash_1 += (ord(s[i]) * cls.P1[i]) % cls.mod1
            s_hash_2 += (ord(s[i]) * cls.P2[i]) % cls.mod2

        return int(s_hash_1), int(s_hash_2)

    @classmethod
    def _load_tree(cls):
        a_tree = set()
        file = open(HASH_FILE, 'r')
        for line in file:
            pair = list(map(int, line.split(' ')))
            a_tree.add((pair[0], pair[1]))
        return a_tree

    @classmethod
    def _save_tree(cls, a_tree):
        f = open(HASH_FILE, 'w')
        for node in a_tree:
            f.write(str(node[0]) + ' ' + str(node[1]) + '\n')
        f.close()

    @classmethod
    def _process_rusmarc(cls, original_file_name, input_data, id, metadata):
        marc_file = os.path.join(current_app.config['UPLOAD_FOLDER'], input_data)
        cur_metadata = cls._get_metadata(marc_file)
        if cur_metadata is None:
            # Write to UPLOAD_ERRORS_LOG: error in record with id
            upload_errors_log = open(UPLOAD_ERRORS_LOG, 'a')
            upload_errors_log.write(original_file_name + ' ' + str(id) + '\n')
            upload_errors_log.close()
            return
        source_database_name, file_encoding = metadata
        source_database_entry = db.session.query(SourceDatabase).filter_by(name=source_database_name).scalar()
        if source_database_entry is None:
            source_database_entry = SourceDatabase(name=source_database_name)

        a_tree = cls._load_tree()

        record_number = 0
        objects_list = []
        with open(marc_file, 'rb') as fh:
            reader = MARCReader(fh, file_encoding=file_encoding)
            for record in reader:
                record_number += 1
                if record:
                    record_string = ''
                    record_string += source_database_entry.name
                    record_table = Record()

                    # Title
                    if record['200'] is not None:
                        if record['200']['a'] is not None:
                            record_table.title = record['200']['a']
                            record_string += record['200']['a']

                    # Document type
                    document_type_entry = db.session.query(DocumentType).filter_by(
                        name=DOCUMENT_TYPES.get(record.leader[7])).scalar()
                    if document_type_entry is not None:
                        record_string += document_type_entry.name
                    else:
                        document_type_entry = DocumentType(name=DOCUMENT_TYPES.get(record.leader[7]))
                        record_string += document_type_entry.name

                    # Publishing year
                    if record['210'] is not None:
                        if record['210']['d'] is not None:
                            record_table.publishing_year = int(record['210']['d'])
                            record_string += record['210']['d']

                    # URL
                    if record['856'] is not None:
                        if record['856']['u'] is not None:
                            record_table.url = record['856']['u']
                            record_string += record['856']['u']

                    # Hashing
                    _hash = cls._hash(record_string)
                    if _hash not in a_tree:
                        a_tree.add(_hash)
                        record_table.hash_1 = str(_hash[0])
                        record_table.hash_2 = str(_hash[1])
                        # db.session.add(document_type_entry)
                        # db.session.add(source_database_entry)
                        objects_list.append(document_type_entry)
                        objects_list.append(source_database_entry)
                        record_table.document_type.append(document_type_entry)
                        record_table.source_database.append(source_database_entry)
                    else:
                        continue

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
                            record_table.isbn = re.sub('\D', '', record['010']['a'])

                    # ISSN
                    if record['011'] is not None:
                        if record['011']['a'] is not None:
                            record_table.issn = re.sub('\D', '', record['011']['a'])

                    # Pages
                    if record['215'] is not None:
                        if record['215']['a'] is not None:
                            temp = re.findall(r'\d+', str(record['215']['a']))
                            if len(temp) != 0:
                                record_table.pages = int(temp[0])

                    # UDC
                    if record['675'] is not None:
                        if record['675']['a'] is not None:
                            record_table.udc = str(record['675']['a'])

                    # BBK
                    if record['686'] is not None:
                        if record['686']['a'] is not None:
                            record_table.bbk = str(record['686']['a'])

                    # Authors
                    if record['700'] is not None:
                        if record['700']['a'] is not None:
                            if record['700']['b'] is not None:
                                author_entry = db.session.query(Author).filter_by(
                                    name=record['700']['a'] + ' ' + record['700']['b']).scalar()
                                if author_entry is not None:
                                    record_table.authors.append(author_entry)
                                    # db.session.add(author_entry)
                                    objects_list.append(author_entry)
                                else:
                                    author_entry = Author(name=record['700']['a'] + ' ' + record['700']['b'])
                                    record_table.authors.append(author_entry)
                                    # db.session.add(author_entry)
                                    objects_list.append(author_entry)
                            elif record['700']['g'] is not None:
                                initials = record['700']['g'].split()
                                for i in range(len(initials)):
                                    initials[i] = initials[i][0] + '.'
                                initials = ' '.join([str(item) for item in initials])
                                author_entry = db.session.query(Author).filter_by(
                                    name=record['700']['a'] + ' ' + initials).scalar()
                                if author_entry is not None:
                                    record_table.authors.append(author_entry)
                                    # db.session.add(author_entry)
                                    objects_list.append(author_entry)
                                else:
                                    author_entry = Author(name=record['700']['a'] + ' ' + initials)
                                    record_table.authors.append(author_entry)
                                    # db.session.add(author_entry)
                                    objects_list.append(author_entry)
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
                                        # db.session.add(author_entry)
                                        objects_list.append(author_entry)
                                    else:
                                        author_entry = Author(name=val)
                                        record_table.authors.append(author_entry)
                                        # db.session.add(author_entry)
                                        objects_list.append(author_entry)
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
                                            # db.session.add(author_entry)
                                            objects_list.append(author_entry)
                                        else:
                                            author_entry = Author(name=val)
                                            record_table.authors.append(author_entry)
                                            # db.session.add(author_entry)
                                            objects_list.append(author_entry)
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
                                    # db.session.add(author_entry)
                                    objects_list.append(author_entry)
                                else:
                                    author_entry = Author(name=val)
                                    record_table.authors.append(author_entry)
                                    # db.session.add(author_entry)
                                    objects_list.append(author_entry)
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
                                        # db.session.add(author_entry)
                                        objects_list.append(author_entry)
                                    else:
                                        author_entry = Author(name=val)
                                        record_table.authors.append(author_entry)
                                        # db.session.add(author_entry)
                                        objects_list.append(author_entry)

                    # Publisher
                    if record['210'] is not None:
                        if record['210']['c'] is not None:
                            publisher_entry = db.session.query(Publisher).filter_by(name=record['210']['c']).scalar()
                            if publisher_entry is not None:
                                # db.session.add(publisher_entry)
                                objects_list.append(publisher_entry)
                                record_table.publisher.append(publisher_entry)
                            else:
                                publisher_entry = Publisher(name=record['210']['c'])
                                record_table.publisher.append(publisher_entry)
                                # db.session.add(publisher_entry)
                                objects_list.append(publisher_entry)

                    # Keywords
                    if record['610'] is not None:
                        if record['610']['a'] is not None:
                            keywords_list = []
                            for f in record.get_fields('610'):
                                keywords_list.append(f['a'].lower())
                            for val in keywords_list:
                                temp = []
                                if '--' in val:
                                    temp = val.split('--')
                                    keywords_list.remove(val)
                                if ',' in val:
                                    temp = val.split(',')
                                    keywords_list.remove(val)
                                for val1 in temp:
                                    if val1 != ' ' and val1 != '':
                                        keywords_list.append(val1.strip())
                            keywords_list = list(set(keywords_list))
                            for val in keywords_list:
                                val = val.replace('"', '')
                                keyword_entry = db.session.query(Keyword).filter_by(name=val).scalar()
                                if keyword_entry is not None:
                                    record_table.keywords.append(keyword_entry)
                                    # db.session.add(keyword_entry)
                                    objects_list.append(keyword_entry)
                                else:
                                    keyword_entry = Keyword(name=val)
                                    record_table.keywords.append(keyword_entry)
                                    # db.session.add(keyword_entry)
                                    objects_list.append(keyword_entry)

                    # TODO: generate bibliographic description
                    record_table.bibliographic_description = None
                    # db.session.add(record_table)
                    objects_list.append(record_table)
                    db.session.add_all(objects_list)



                elif isinstance(reader.current_exception, exc.FatalReaderError):
                    # data file format error
                    # reader will raise StopIteration
                    upload_errors_log = open(UPLOAD_ERRORS_LOG, 'a')
                    # upload_errors_log.write(str(original_file_name) + ' ' + str(id) + '\n')
                    upload_errors_log.write(str(reader.current_exception) + '\n')
                    # upload_errors_log.write(str(reader.current_chunk) + '\n')
                    upload_errors_log.close()
                else:
                    # fix the record data, skip or stop reading:
                    upload_errors_log = open(UPLOAD_ERRORS_LOG, 'a')
                    # upload_errors_log.write(str(original_file_name) + ' ' + str(id) + '\n')
                    upload_errors_log.write(str(reader.current_exception) + '\n')
                    # upload_errors_log.write(str(reader.current_chunk) + '\n')
                    upload_errors_log.close()
                    # break/continue/raise
                    continue
        cls._save_tree(a_tree)

    @classmethod
    def _process_marc21(cls, original_file_name, input_data, id, metadata):
        marc_file = os.path.join(current_app.config['UPLOAD_FOLDER'], input_data)
        cur_metadata = cls._get_metadata(marc_file)
        if cur_metadata is None:
            # Write to UPLOAD_ERRORS_LOG: error in record with id
            upload_errors_log = open(UPLOAD_ERRORS_LOG, 'a')
            upload_errors_log.write(original_file_name + ' ' + str(id) + '\n')
            upload_errors_log.close()
            return
        source_database_name, file_encoding = metadata
        source_database_entry = db.session.query(SourceDatabase).filter_by(name=source_database_name).scalar()
        if source_database_entry is None:
            source_database_entry = SourceDatabase(name=source_database_name)

        a_tree = cls._load_tree()

        record_number = 0
        objects_list = []
        with open(marc_file, 'rb') as fh:
            reader = MARCReader(fh, file_encoding=file_encoding)
            for record in reader:
                record_number += 1
                if record:
                    record_string = ''
                    record_string += source_database_entry.name
                    record_table = Record()

                    # Title
                    if record.title() is not None:
                        record_table.title = record.title()
                        record_string += record.title()

                    # Document type
                    document_type_entry = db.session.query(DocumentType).filter_by(
                        name=DOCUMENT_TYPES.get(record.leader[7])).scalar()
                    if document_type_entry is not None:
                        record_string += document_type_entry.name
                    else:
                        document_type_entry = DocumentType(name=DOCUMENT_TYPES.get(record.leader[7]))
                        record_string += document_type_entry.name

                    # Publishing year
                    if record['260'] is not None:
                        if record['260']['c'] is not None:
                            record_table.publishing_year = record['260']['c']
                            record_string += str(record['260']['c'])

                    # URL
                    if record['856'] is not None:
                        if record['856']['u'] is not None:
                            record_table.url = record['856']['u']
                            record_string += record['856']['u']
                    elif record['003'] is not None:
                        record_table.url = record['003']
                        record_string += record['003']

                    # Hashing
                    _hash = cls._hash(record_string)
                    if _hash not in a_tree:
                        a_tree.add(_hash)
                        # db.session.add(document_type_entry)
                        # db.session.add(source_database_entry)
                        objects_list.append(document_type_entry)
                        objects_list.append(source_database_entry)

                        record_table.hash_1 = _hash[0]
                        record_table.hash_2 = _hash[1]
                        record_table.document_type.append(document_type_entry)
                        record_table.source_database.append(source_database_entry)
                    else:
                        continue

                    # Description
                    if record['520'] is not None:
                        if record['520']['a'] is not None:
                            record_table.description = str(record['520']['a'])

                    # Cover
                    if record['856'] is not None:
                        if record['856']['x'] is not None:
                            record_table.cover = record['856']['x']

                    # ISBN
                    if record.isbn() is not None:
                        record_table.isbn = record.isbn()

                    # ISSN
                    if record.issn() is not None:
                        record_table.issn = record.issn()

                    # Pages
                    if record['300'] is not None:
                        if record['300']['a'] is not None:
                            temp = re.findall(r'\d+', str(record['300']['a']))
                            record_table.pages = int(temp[0])

                    # UDC
                    if record['080'] is not None:
                        if record['080']['a'] is not None:
                            record_table.udc = str(record['080']['a'])

                    # BBK
                    if record['084'] is not None:
                        if record['084']['a'] is not None:
                            record_table.bbk = record['084']['a']

                    # Authors
                    if record['100'] is not None:
                        if record['100']['a'] is not None:
                            author_entry = db.session.query(Author).filter_by(name=record['100']['a']).scalar()
                            if author_entry is not None:
                                record_table.authors.append(author_entry)
                                # db.session.add(author_entry)
                                objects_list.append(author_entry)
                            else:
                                author_entry = Author(name=record['100']['a'])
                                record_table.authors.append(author_entry)
                                # db.session.add(author_entry)
                                objects_list.append(author_entry)
                    if record['700'] is not None:
                        if record['700']['a'] is not None:
                            authors_list = []
                            for f in record.get_fields('700'):
                                authors_list.append(f['a'])
                            for val in authors_list:
                                author_entry = db.session.query(Author).filter_by(name=val).scalar()
                                if author_entry is not None:
                                    record_table.authors.append(author_entry)
                                    # db.session.add(author_entry)
                                    objects_list.append(author_entry)
                                else:
                                    author_entry = Author(name=val)
                                    record_table.authors.append(author_entry)
                                    # db.session.add(author_entry)
                                    objects_list.append(author_entry)

                    # Publisher
                    if record['260'] is not None:
                        if record['260']['b'] is not None:
                            publisher_entry = db.session.query(Publisher).filter_by(name=record.publisher()).scalar()
                            if publisher_entry is not None:
                                # db.session.add(publisher_entry)
                                objects_list.append(publisher_entry)
                                record_table.publisher.append(publisher_entry)
                            else:
                                publisher_entry = Publisher(name=record.publisher())
                                record_table.publisher.append(publisher_entry)
                                # db.session.add(publisher_entry)
                                objects_list.append(publisher_entry)

                    # Keywords
                    if record['653'] is not None:
                        if record['653']['a'] is not None:
                            keywords_list = []
                            for f in record.get_fields('653'):
                                keywords_list.append(f['a'].lower())
                            for val in keywords_list:
                                temp = []
                                if '--' in val:
                                    temp = val.split('--')
                                    keywords_list.remove(val)
                                if ',' in val:
                                    temp = val.split(',')
                                    keywords_list.remove(val)
                                for val1 in temp:
                                    if val1 != ' ' and val1 != '':
                                        keywords_list.append(val1.strip())
                            keywords_list = list(set(keywords_list))
                            for val in keywords_list:
                                val = val.replace('"', '')
                                keyword_entry = db.session.query(Keyword).filter_by(name=val).scalar()
                                if keyword_entry is not None:
                                    record_table.keywords.append(keyword_entry)
                                    # db.session.add(keyword_entry)
                                    objects_list.append(keyword_entry)
                                else:
                                    keyword_entry = Keyword(name=val)
                                    record_table.keywords.append(keyword_entry)
                                    # db.session.add(keyword_entry)
                                    objects_list.append(keyword_entry)

                    # TODO: generate bibliographic description
                    record_table.bibliographic_description = None
                    # db.session.add(record_table)
                    objects_list.append(record_table)
                    db.session.add_all(objects_list)
                elif isinstance(reader.current_exception, exc.FatalReaderError):
                    # data file format error
                    # reader will raise StopIteration
                    upload_errors_log = open(UPLOAD_ERRORS_LOG, 'a')
                    # upload_errors_log.write(str(original_file_name) + ' ' + str(id) + '\n')
                    upload_errors_log.write(str(reader.current_exception) + '\n')
                    # upload_errors_log.write(str(reader.current_chunk) + '\n')
                    upload_errors_log.close()
                else:
                    # fix the record data, skip or stop reading:
                    upload_errors_log = open(UPLOAD_ERRORS_LOG, 'a')
                    # upload_errors_log.write(str(original_file_name) + ' ' + str(id) + '\n')
                    upload_errors_log.write(str(reader.current_exception) + '\n')
                    # upload_errors_log.write(str(reader.current_chunk) + '\n')
                    upload_errors_log.close()
                    # break/continue/raise
                    continue
        cls._save_tree(a_tree)

    @classmethod
    def upload_to_database(cls):
        directory = str(current_app.config['UPLOAD_FOLDER'])
        # num_workers = cpu_count()

        file_to_encoding = {}
        max_part_size = 1000
        for filename in os.listdir(directory):
            if os.stat(os.path.join(directory, filename)).st_size > 5000000:
                cur_file_path = os.path.join(directory, filename)
                metadata = cls._get_metadata(cur_file_path)

                file = open(cur_file_path, 'r', encoding=metadata[1])

                cur_part_size = 0
                part_id = 0

                cur_part = ''
                for c in file.read():
                    cur_part += c
                    if ord(c) == 29:
                        cur_part_size += 1
                    if cur_part_size == max_part_size:
                        new_file_name = filename + '_PART_' + str(part_id) + '.iso'
                        new_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                                                'uploads/', new_file_name))
                        file_to_encoding[new_file_name] = metadata
                        with open(new_file, 'w+', encoding=metadata[1]) as output:
                            output.write(cur_part)
                        output.close()
                        cur_part = ''
                        cur_part_size = 0
                        part_id += 1
                if len(cur_part) > 0:
                    new_file_name = filename + '_PART_' + str(part_id) + '.iso'
                    new_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                                            'uploads/', new_file_name))
                    file_to_encoding[new_file_name] = metadata
                    with open(new_file, 'w+', encoding=metadata[1]) as output:
                        output.write(cur_part)
                    output.close()
                    part_id += 1
                os.remove(cur_file_path)

        for filename in os.listdir(directory):

            cur_file_path = os.path.join(directory, filename)

            metadata = None
            if filename in file_to_encoding:
                metadata = file_to_encoding[filename]
            else:
                metadata = cls._get_metadata(cur_file_path)
            source_db_name = metadata[0]

            original_file_name = filename
            id = 1

            num = ''
            pos = len(filename) - 5
            while pos >= 0:
                if '0' <= filename[pos] <= '9':
                    num = filename[pos] + num
                    pos -= 1
                else:
                    break

            if pos - 5 >= 0 and filename[pos - 5:pos + 1] == '_PART_':
                id = int(num) * max_part_size + 1
                original_file_name = filename[:pos - 5]

            file = open(cur_file_path, 'r', encoding=metadata[1])
            cur_record = ''
            for c in file.read():
                cur_record += c
                if ord(c) == 29:
                    with open(TEMP_FILE, 'w+', encoding=metadata[1]) as output:
                        output.write(cur_record)
                    output.close()

                    if source_db_name == 'Издательство Лань' or source_db_name == 'RUCONT':
                        # procs = [
                        #     Process(target= cls._process_rusmarc, args=(original_file_name, TEMP_FILE, id, metadata)) for i in range(num_workers)]
                        # for p in procs:
                        #     p.start()
                        #
                        # for p in procs:
                        #     p.join()
                        cls._process_rusmarc(original_file_name, TEMP_FILE, id, metadata)

                    elif source_db_name == 'ИКО Юрайт':
                        # procs = [
                        #     Process(target=cls._process_marc21, args=(original_file_name, TEMP_FILE, id, metadata)) for i in range(num_workers)]
                        # for p in procs:
                        #     p.start()
                        #
                        # for p in procs:
                        #     p.join()
                        cls._process_marc21(original_file_name, TEMP_FILE, id, metadata)

                    cur_record = ''
                    id += 1
            Record.reindex()
            db.session.commit()

            os.remove(cur_file_path)

        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)

    @classmethod
    def get_upload_errors(cls):
        if os.path.getsize(UPLOAD_ERRORS_LOG) > 0:
            errors_list = []
            with open(UPLOAD_ERRORS_LOG) as log:
                for line in log:
                    errors_list.append(line)
            open(UPLOAD_ERRORS_LOG, 'w').close()
            return errors_list
        else:
            return None
