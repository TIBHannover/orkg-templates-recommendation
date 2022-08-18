from elasticsearch import Elasticsearch

from src.models.elasticsearch.document import DocumentCreator
from src.util.io import Reader

es = Elasticsearch(hosts=['localhost:9200'])

__INDEX_NAME__ = 'templates'


def recreate_index(training_set_path):
    es.indices.delete(index=__INDEX_NAME__, ignore=[400, 404])

    return create_index(training_set_path)


def create_index(training_set_path):
    es.indices.create(index=__INDEX_NAME__, ignore=[400, 404])
    indexed_documents = 0
    not_indexed = []

    # TODO: can we build the index directly from the triplestore ?
    data = Reader.read_json(training_set_path)
    for instance in data['entailments'] + data['neutrals']:

        text = '{} {}'.format(instance['premise'], instance['hypothesis'])
        es.index(index=__INDEX_NAME__, id=instance['instance_id'], body={'text': DocumentCreator.postprocess(text)})
        indexed_documents += 1

    return {
        'indexedDocuments': indexed_documents,
        'documents': len(data['entailments'] + data['neutrals']),
        'notIndexedDocuments': not_indexed
    }


def query_index(q, top_k=5):
    query = DocumentCreator.postprocess(q, is_query=True)

    if not query:
        return {}

    body = '{"query": { "match" : { "text" : { "query" : "' + query + '" } } }, "size":' + str(top_k * 2) + '}'
    interm_results = es.search(index=__INDEX_NAME__, body=body, track_scores=True)

    try:
        similar = {hit["_id"]: hit["_score"] for hit in interm_results["hits"]["hits"]}

        for key in similar.keys():
            # The first result will always have a score of 1.0
            similar[key] = similar[key] / interm_results['hits']['max_score']

        return {k: v for k, v in similar.items()}

    except KeyError:
        return {}
