import os

from src import MODELS_DIR
from src.util.io import Reader, Writer


def create_templates_fields_map(training_set_path, full=False):
    """
    :param training_set_path: must point to the dataset that has a templates list.
    """
    dataset = Reader.read_json(training_set_path)

    baseline_map = {}
    for template in dataset['templates']:
        for research_field in template['research_fields']:

            if not research_field['id']:
                continue

            if research_field['id'] not in baseline_map:
                baseline_map[research_field['id']] = [template['id']]
            else:
                baseline_map[research_field['id']].append(template['id'])

    if full:
        Writer.write_json(baseline_map, os.path.join(MODELS_DIR, 'baseline_full.json'))
    else:
        Writer.write_json(baseline_map, os.path.join(MODELS_DIR, 'baseline.json'))

    print('model stored in {}'.format(MODELS_DIR))

    return {
        'n_research_fields': len(baseline_map),
        'n_templates': len(dataset['templates'])
    }


def query(q, full=False):
    """
    :param q: must be a research field ID
    """

    if full:
        baseline_map = Reader.read_json(os.path.join(MODELS_DIR, 'baseline_full.json'))
    else:
        baseline_map = Reader.read_json(os.path.join(MODELS_DIR, 'baseline.json'))

    if q in baseline_map:
        return baseline_map[q]

    return [None]  # important for the evaluation
