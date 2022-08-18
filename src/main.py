from argparse import ArgumentParser

from src.data import main as data
from src.models import train, evaluate, predict


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-t', '--task',
                        choices=['dataset', 'train', 'evaluate', 'predict'],
                        required=True,
                        help='Indicates the task to be executed. '
                             'dataset: fetches, analyses and splits the dataset. The file paths are fixed. '
                             'train: trains the provided approach using the provided training set. '
                             'evaluate: evaluates the provided approach using the provided test set. '
                             'predict: predicts the provided approach using the provided query.'
                        )

    parser.add_argument('-a', '--approach',
                        choices=['elasticsearch', 'scibert', 'baseline', 'baseline_full'],
                        required=False,
                        help='Indicates the approach to do the task on.'
                        )

    parser.add_argument('-trainp', '--training_set_path',
                        type=str,
                        required=False,
                        help='Path to training set.'
                        )

    parser.add_argument('-testp', '--test_set_path',
                        type=str,
                        required=False,
                        help='Path to test set.'
                        )

    parser.add_argument('-q', '--query',
                        type=str,
                        required=False,
                        help='Paper textual representation. A concatenation of paper\'s title and DOI. '
                        )

    parser.add_argument('-n', '--n_results',
                        type=int,
                        default=20,
                        required=False,
                        help='Number of results to be retrieved.'
                        )
    return parser.parse_args()


def main():
    args = parse_args()

    {
        'dataset': data.main,
        'train': train.main,
        'evaluate': evaluate.main,
        'predict': predict.main
    }[args.task](args)


if __name__ == '__main__':
    main()
