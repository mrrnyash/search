from app.models import *
import re

class Search:

    def _is_filled(self, data):
        if data is None:
            return False
        if data == '':
            return False
        if not data:
            return False
        return True

    def find_records(self, formdata):
        results = []
        results.append(Record.query.filter(Record.title.like('%{}%'.format(formdata.search_request.data))))
        return results