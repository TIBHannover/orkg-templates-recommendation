import os

import pandas as pd

from src import TRIPLE_STORE_URL, RAW_DATA_DIR
from src.data.sparql.queries import TEMPLATED_PAPERS
from src.data.sparql.service import query
from src.util.io import Writer
from src.util.string import id_to_uri

PAPERS_PER_TEMPLATE_THRESHOLD = 2


def to_json(df, papers_dump):
    uri_columns = ['template', 'templateComponentProperty', 'templateOfResearchField', 'paper', 'paper_research_field']
    df[uri_columns] = df[uri_columns].applymap(lambda x: os.path.basename(str(x)))

    templated_papers = []
    paper_columns = ['paper', 'paper_label', 'paper_research_field', 'paper_research_field_label', 'doi']
    for template_id in df.template.unique():
        template_df = df[df.template == template_id]

        template_json = {
            'id': template_df.template.iloc[0],
            'label': template_df.templateLabel.iloc[0],
            'research_fields': [
                {'id': id, 'label': label}
                for (i, (id, label)) in template_df.loc[:, ['templateOfResearchField', 'templateOfResearchFieldLabel']
                                        ].dropna().drop_duplicates().iterrows()
            ],
            'properties': template_df.templateComponentPropertyLabel.unique().tolist(),
            'papers': [
                {
                    'id': row[0],
                    'label': row[1],
                    'doi': row[4],
                    'research_field': {
                        'id': row[2],
                        'label': row[3]
                    },
                    'abstract': papers_dump[papers_dump.uri == id_to_uri(row[0])].processed_abstract.iloc[0]
                }
                for (i, row) in template_df.loc[:, paper_columns].drop_duplicates().iterrows()
                if len(papers_dump[papers_dump.uri == id_to_uri(row[0])].processed_abstract.index) != 0
                   and papers_dump[papers_dump.uri == id_to_uri(row[0])].processed_abstract.iloc[0]
            ]
        }
        templated_papers.append(template_json)

    # filtering based on n_papers per template #
    filtered_templated_papers = []
    templated_paper_ids = []
    for template in templated_papers:
        if len(template['papers']) >= PAPERS_PER_TEMPLATE_THRESHOLD:
            filtered_templated_papers.append(template)

        for paper in template['papers']:
            templated_paper_ids.append(paper['id'])

    return filtered_templated_papers, list(set(templated_paper_ids))


def main():
    # TODO: automatically download the orkg_papers dump
    df = query(TRIPLE_STORE_URL, TEMPLATED_PAPERS)
    papers_dump = pd.read_csv(os.path.join(RAW_DATA_DIR, 'orkg_papers.csv')).fillna('')
    templated_papers, templated_paper_ids = to_json(df, papers_dump)
    Writer.write_json({'templates': templated_papers}, os.path.join(RAW_DATA_DIR, 'templated_papers.json'))

    return templated_papers, templated_paper_ids


if __name__ == '__main__':
    main()
