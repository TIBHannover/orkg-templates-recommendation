import pandas as pd

from io import StringIO
from SPARQLWrapper import SPARQLWrapper, CSV


def query(endpoint_url, sparql_query):
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(CSV)

    results = sparql.query().convert()

    try:
        results = results.decode('utf-8')
    except UnicodeDecodeError:
        results = results.decode('latin-1')

    _csv = StringIO(results)
    return pd.read_csv(_csv, sep=',').fillna('')
