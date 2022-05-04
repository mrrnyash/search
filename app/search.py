from models import *
from app import db
from forms import SearchForm


class Search:

    def get_results(self, request_data):
        results = list(Record())


        return results