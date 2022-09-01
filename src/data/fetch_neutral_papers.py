import os
import pandas as pd

from src import TRIPLE_STORE_URL, RAW_DATA_DIR, ORKG_PAPERS_DUMP_URL
from src.data import fetch_templated_papers
from src.data.sparql.queries import PAPERS_BY_RESEARCH_FIELD_QUERY, PAPERS_QUERY
from src.data.sparql.service import query
from src.util.io import Writer
from src.util.string import id_to_uri, uri_to_id


def extract_papers_research_fields(templated_papers):
    research_fields = {}

    for template in templated_papers:
        for paper in template['papers']:

            if paper['research_field']['id'] not in research_fields:
                research_fields[paper['research_field']['id']] = {'label': '', 'papers': []}

            research_fields[paper['research_field']['id']]['label'] = paper['research_field']['label']
            research_fields[paper['research_field']['id']]['papers'].append(paper['id'])

    return research_fields


def fetch_neutral_papers_with_same_distribution(paper_ids, research_fields, papers_dump):
    neutral_papers = []
    neutral_paper_ids = []

    for research_field_id in list(research_fields.keys()):
        orkg_papers = query(TRIPLE_STORE_URL,
                            PAPERS_BY_RESEARCH_FIELD_QUERY('<{}>'.format(id_to_uri(research_field_id)))
                            )

        temp_neutral_papers = []
        temp_neutral_paper_ids = []

        for index, orkg_paper in orkg_papers.iterrows():

            # stop if we got what we need
            if len(temp_neutral_papers) == len(research_fields[research_field_id]['papers']):
                break

            # papers don't use templates and have not been seen before
            # only consider english papers
            if orkg_paper.loc['paper'] in paper_ids + neutral_paper_ids + temp_neutral_paper_ids:
                continue

            if len(papers_dump[papers_dump.uri == orkg_paper.loc['paper']].processed_abstract) != 0 \
                    and papers_dump[papers_dump.uri == orkg_paper.loc['paper']].processed_abstract.iloc[0]:

                temp_neutral_paper = {
                    'id': uri_to_id(orkg_paper.loc['paper']),
                    'label': orkg_paper.loc['paper_title'],
                    'doi': orkg_paper.loc['doi'],
                    'research_field': {
                        'id': research_field_id,
                        'label': research_fields[research_field_id]['label']
                    },
                    'abstract': papers_dump[papers_dump.uri == orkg_paper.loc['paper']].processed_abstract.iloc[0]
                }

                temp_neutral_papers.append(temp_neutral_paper)
                temp_neutral_paper_ids.append(orkg_paper.loc['paper'])

        neutral_papers.extend(temp_neutral_papers)
        neutral_paper_ids.extend(temp_neutral_paper_ids)

    return neutral_papers, neutral_paper_ids


def fetch_rest_neutral_papers(paper_ids, neutral_paper_ids, papers_dump):
    rest_neutral_papers = []
    rest_neutral_paper_ids = []

    orkg_papers = query(TRIPLE_STORE_URL, PAPERS_QUERY)

    while len(rest_neutral_papers) + len(neutral_paper_ids) < len(paper_ids):
        orkg_paper = orkg_papers.sample(n=1).iloc[0]

        # papers don't use templates and have not been seen before
        if orkg_paper.loc['paper'] in paper_ids + neutral_paper_ids + rest_neutral_paper_ids:
            continue

        if len(papers_dump[papers_dump.uri == orkg_paper.loc['paper']].processed_abstract) != 0 \
                and papers_dump[papers_dump.uri == orkg_paper.loc['paper']].processed_abstract.iloc[0]:
            neutral_paper = {
                'id': uri_to_id(orkg_paper.loc['paper']),
                'label': orkg_paper.loc['paper_title'],
                'doi': orkg_paper.loc['doi'],
                'research_field': {
                    'id': uri_to_id(orkg_paper.loc['research_field']),
                    'label': orkg_paper.loc['research_field_label']
                },
                'abstract': papers_dump[papers_dump.uri == orkg_paper.loc['paper']].processed_abstract.iloc[0]
            }

            print('{}/{}'.format(len(rest_neutral_papers) + len(neutral_paper_ids) + 1, len(paper_ids)))
            rest_neutral_papers.append(neutral_paper)
            rest_neutral_paper_ids.append(orkg_paper.loc['paper'])

    return rest_neutral_papers, rest_neutral_paper_ids


def main(templated_papers, templated_paper_ids, papers_dump):
    research_fields = extract_papers_research_fields(templated_papers)

    # papers that do not use any template and have the same distribution as the previous papers
    neutral_papers, neutral_paper_ids = fetch_neutral_papers_with_same_distribution(
        templated_paper_ids, research_fields, papers_dump
    )

    # papers that do not use any template and have a different distribution as the previous papers
    rest_neutral_papers, rest_neutral_paper_ids = fetch_rest_neutral_papers(
        templated_paper_ids, neutral_paper_ids, papers_dump
    )

    neutral_papers += rest_neutral_papers
    neutral_paper_ids += rest_neutral_paper_ids

    Writer.write_json({'neutral_papers': neutral_papers}, os.path.join(RAW_DATA_DIR, 'neutral_papers.json'))

    return neutral_papers, list(set(neutral_paper_ids))


if __name__ == '__main__':
    dump = pd.read_csv(ORKG_PAPERS_DUMP_URL).fillna('')
    papers, paper_ids = fetch_templated_papers.main(dump)
    main(papers, paper_ids, dump)
