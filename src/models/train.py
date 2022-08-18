from argparse import ArgumentParser

import src.models.elasticsearch.service as es
import src.models.baseline.service as baseline


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-a', '--approach',
                        choices=['elasticsearch', 'scibert', 'baseline', 'baseline_full'],
                        required=True,
                        help='Indicates the approach to evaluate.'
                        )

    parser.add_argument('-trainp', '--training_set_path',
                        type=str,
                        required=False,
                        help='Path to training set.'
                        )

    return parser.parse_args()


def train_elasticsearch(training_set_path):
    return es.recreate_index(training_set_path)


def train_scibert(training_set_path):
    raise NotImplementedError


def train_baseline(training_set_path):
    return baseline.create_templates_fields_map(training_set_path)


def train_baseline_full(training_set_path):
    return baseline.create_templates_fields_map(training_set_path, full=True)


def main(config=None):
    args = config or parse_args()

    assert args.approach, 'approach must be provided.'
    assert args.training_set_path, 'training_set_path must be provided.'

    print('Building Elasticsearch Index...')
    info = {
        'elasticsearch': train_elasticsearch,
        'scibert': train_scibert,
        'baseline': train_baseline,
        'baseline_full': train_baseline_full
    }[args.approach](args.training_set_path)
    print(info)


if __name__ == '__main__':
    main()
