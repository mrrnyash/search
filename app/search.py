from flask import current_app


class Search:

    def _is_filled(self, data):
        if data is None:
            return False
        if data == '':
            return False
        if not data:
            return False
        return True

    # def _find_records(self, formdata):
    #     results = []
    #     results.append(Record.query.filter(Record.title.like('%{}%'.format(formdata.search_request.data))))
    #     return results

    def add_to_index(self, index, model):
        if not current_app.elasticsearch:
            return
        payload = {}
        for field in model.__searchable__:
            payload[field] = getattr(model, field)
        current_app.elasticsearch.index(index=index, id=model.id, document=payload)

    def remove_from_index(self, index, model):
        if not current_app.elasticsearch:
            return
        current_app.elasticsearch.delete(index=index, id=model.id)

    def query_index(self, index, query, page, per_page):
        if not current_app.elasticsearch:
            return [], 0
        search = current_app.elasticsearch.search(
            index=index,
            query={'multi_match': {'query': query, 'fields': ['*']},
                   'from': (page - 1) * per_page, 'size': per_page})
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        return ids, search['hits']['total']
