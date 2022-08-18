from argparse import ArgumentParser

import src.models.elasticsearch.service as es
import src.models.baseline.service as baseline
from src.models.scibert.service import TemplateSimilarityPredictor


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-a', '--approach',
                        choices=['elasticsearch', 'scibert', 'baseline', 'baseline_full'],
                        required=True,
                        help='Indicates the approach to evaluate.'
                        )

    parser.add_argument('-q', '--query',
                        type=str,
                        required=True,
                        help='Paper textual representation. A concatenation of paper\'s title and DOI. '
                        )

    parser.add_argument('-n', '--n_results',
                        type=int,
                        default=20,
                        required=False,
                        help='Number of results to be retrieved.'
                        )
    return parser.parse_args()


def predict_elasticsearch(q, n_results=20):
    results = []
    similar_templates = es.query_index(q, top_k=n_results)

    if not similar_templates:
        return results

    template_ids = []
    for similar_template, similar_score in similar_templates.items():

        if 'x' in similar_template:
            template_id = similar_template[:similar_template.find('x')]
        else:
            template_id = None

        if template_id not in template_ids:
            results.append({
                'template_id': template_id,
                'score': similar_score
            })
            template_ids.append(template_id)

    return results[:n_results]


def predict_scibert(q, n_results=20):
    predictor = TemplateSimilarityPredictor.get_instance()
    similar_templates = predictor.predict_similar_templates(q)

    return similar_templates[:n_results]


def predict_baseline(q, n_results=20):
    similar_templates = baseline.query(q)

    results = []
    for template in similar_templates:
        results.append({
            'template_id': template
        })

    return results[:n_results]


def predict_baseline_full(q, n_results=20):
    similar_templates = baseline.query(q, full=True)

    results = []
    for template in similar_templates:
        results.append({
            'template_id': template
        })

    return results[:n_results]


def main(config=None):
    args = config or parse_args()

    assert args.approach, 'approach must be provided.'
    assert args.query, 'query must be provided.'
    assert args.n_results, 'n_results must be provided'

    print('Querying...')
    results = {
        'elasticsearch': predict_elasticsearch,
        'scibert': predict_scibert,
        'baseline': predict_baseline,
        'baseline_full': predict_baseline_full
    }[args.approach](args.query, args.n_results)

    print(results)


if __name__ == '__main__':
    main()
