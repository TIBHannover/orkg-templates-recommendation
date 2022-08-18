import os

from src import PROCESSED_DATA_DIR
from src.data import fetch_templated_papers, fetch_baseline_templates
from src.data import fetch_neutral_papers
from src.util.io import Writer


def main():
    fetch_baseline_templates.main()
    templated_papers, templated_paper_ids = fetch_templated_papers.main()
    neutral_papers, neutral_paper_ids = fetch_neutral_papers.main(templated_papers, templated_paper_ids)

    dataset = {'templates': templated_papers, 'neutral_papers': neutral_papers}
    Writer.write_json(
        dataset,
        os.path.join(PROCESSED_DATA_DIR, 'dataset.json')
    )

    return dataset


if __name__ == '__main__':
    main()
