from app.main.marc_processor import MARCProcessor


marc_processor = MARCProcessor()

# TODO: find a way to check the actual format of the MARC file

def process_data_unimarc(input_data):
    marc_processor.process_rusmarc(input_data)


def process_data_marc21(input_data):
    marc_processor.process_marc21(input_data)
