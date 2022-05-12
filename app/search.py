from flask import current_app
import json
import re
import datetime

now = datetime.datetime.now()


def add_to_index(index, model):
    if not current_app.elasticsearch:
        # TODO: add fallback
        return
    payload = {}

    for field in model.__searchable__:
        if field == 'authors' or field == 'keywords' or field == 'source_database' or field == 'document_type':
            objects = getattr(model, field)
            payload[field] = [attr.name for attr in objects]
        else:
            payload[field] = getattr(model, field)

    current_app.elasticsearch.index(index=index, id=model.id, body=payload)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id)

def query_index(index, formdata, page, per_page):
    if not current_app.elasticsearch:
        return [], 0

    mylist = []

    if formdata['q'] is not None and len(formdata['q']) != 0:
        mylist.append({"multi_match":{"query":  formdata['q']}})
    if formdata['title'] is not None and len(formdata['title']) != 0:
        mylist.append({"match":{"title":  formdata['title']}})
    if formdata['author'] is not None and len(formdata['author']) != 0:
        mylist.append({"match":{"authors":  formdata['author']}})
    if formdata['isbn_issn_doi'] is not None and len(formdata['isbn_issn_doi']) != 0:
        isbn = re.sub('[^0-9]', '', formdata['isbn_issn_doi'])
        mylist.append({"match":{"isbn":  isbn}})

    allfilters = []

    lstkeys = []
    keysfilters = {}
    myshouldkeys = {}
    keys = []
    if formdata['keywords'] is not None and len(formdata['keywords']) != 0:
        keylst = re.split(' |, |,|;|; ', formdata['keywords'])
        for key in keylst:
            keys.append({"match":{"keywords":  key}})
        myshouldkeys["must"] = keys
        keysfilters["bool"] = myshouldkeys
        allfilters.append(keysfilters)

    lstyears = []
    yearsfilters = {}
    myshouldyears = {}
    years = []
    if formdata['pubyear1'] is not None or formdata['pubyear2'] is not None:
        pubyears = []
        if formdata['pubyear1'] is not None and formdata['pubyear2'] is not None:
            pubyears = [*range(formdata['pubyear1'], formdata['pubyear2'] + 1, 1)]
        elif formdata['pubyear1'] is not None:
            pubyears = [*range(formdata['pubyear1'], now.year, 1)]
        else:
            pubyears = [*range(1900, formdata['pubyear2'] + 1, 1)]

        for year in pubyears:
            years.append({"match": {"publishing_year": year}})
        myshouldyears["should"] = years
        yearsfilters["bool"] = myshouldyears
        allfilters.append(yearsfilters)

    lstbase = []
    basefilters = {}
    myshouldbase = {}
    base = []
    if len(formdata['source_database']) != 0:
        basenames = [ getattr(attr,'name') for attr in formdata['source_database']]
        for basename in basenames:
            base.append({"match":{"source_database":  basename}})
        myshouldbase["should"] = base
        basefilters["bool"] = myshouldbase
        allfilters.append(basefilters)

    lstdoc = []
    docfilters = {}
    myshoulddoc = {}
    doc = []
    if len(formdata['document_type']) != 0:
        docnames = [getattr(attr,'name') for attr in formdata['document_type']]
        for docname in docnames:
            doc.append({"match":{"document_type":  docname}})
        myshoulddoc["should"] = doc
        docfilters["bool"] = myshoulddoc
        allfilters.append(docfilters)

    mymust = {}
    mymust["must"] = mylist
    mymust["filter"] = allfilters
    mybool = {}
    mybool["bool"] = mymust
    myquery = { }

    myquery["from"] = (page - 1) * per_page
    myquery["size"] = per_page
    myquery["query"] = mybool

    search = current_app.elasticsearch.search(index=index, body=json.dumps(myquery))
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    return ids, search['hits']['total']['value']
