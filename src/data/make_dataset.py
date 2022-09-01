import os

import pandas as pd

from src import PROCESSED_DATA_DIR, ORKG_PAPERS_DUMP_URL
from src.data import fetch_templated_papers, fetch_baseline_templates
from src.data import fetch_neutral_papers
from src.util.io import Writer


def extract_premises(templated_papers):
    premises = []
    for template in templated_papers:
        premise = '{} {}'.format(
            template['label'],
            ' '.join([property for property in template['properties']])
        )

        premises.append({
            'id': template['id'],
            'label': template['label'],
            'premise': premise
        })

    return premises


def main():
    fetch_baseline_templates.main()

    papers_dump = pd.read_csv(ORKG_PAPERS_DUMP_URL).fillna('')
    templated_papers, templated_paper_ids = fetch_templated_papers.main(papers_dump)
    neutral_papers, neutral_paper_ids = fetch_neutral_papers.main(templated_papers, templated_paper_ids, papers_dump)

    dataset = {'templates': templated_papers, 'neutral_papers': neutral_papers}
    Writer.write_json(
        dataset,
        os.path.join(PROCESSED_DATA_DIR, 'dataset.json')
    )

    dataset_premises = extract_premises(templated_papers)
    Writer.write_json(
        {'templates': dataset_premises},
        os.path.join(PROCESSED_DATA_DIR, 'dataset_premises.json')
    )

    return dataset


if __name__ == '__main__':
    main()
