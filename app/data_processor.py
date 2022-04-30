from app.models import *
from app.marc_processor import MARCProcessor


class DataProcessor:
    marc = MARCProcessor()

    # TODO: find a way to check the actual format of the MARC file
    def process_data_unimarc(self, input_data):
        self.marc.process_rusmarc(input_data)

    def process_data_marc21(self, input_data):
        self.marc.process_marc21(input_data)
