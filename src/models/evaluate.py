import os
from argparse import ArgumentParser

from src.models import predict, train
from src.util.io import Reader, Writer
from src.util.string import extend_path
from src.util.visualization import plot_research_fields_f_measures


def parse_args():
    parser = ArgumentParser()

    parser.add_argument('-a', '--approach',
                        choices=['elasticsearch', 'scibert', 'baseline', 'baseline_full'],
                        required=True,
                        help='Indicates the approach to evaluate.'
                        )

    parser.add_argument('-testp', '--test_set_path',
                        type=str,
                        required=True,
                        help='Path to test set.'
                        )
    return parser.parse_args()


def evaluate_elasticsearch(test_set_path):
    test_set = Reader.read_json(test_set_path)

    # including the neutral template
    n_templates = len(list(set([entailment['template_id'] for entailment in test_set['entailments']]))) + 1

    accuracy = 0
    tp = 0
    fp = 0
    instances = test_set['entailments'] + test_set['contradictions'] + test_set['neutrals']
    research_fields = init_research_fields_metrics(instances)

    for i, instance in enumerate(instances):
        print('{}/{} - instance {}'.format(i + 1, len(instances), instance['instance_id']))
        instance['results'] = predict.predict_elasticsearch(instance['hypothesis'])

        elasticsearch_entailments = instance['results'][:1]  # ignore fp
        elasticsearch_results = extract_top_k_results(instance['results'], 1)

        # ES doesn't differentiate between neutrals and entailments
        if instance['template_id'] in elasticsearch_results:
            accuracy += n_templates - len(elasticsearch_entailments) + 1
            tp += 1
            fp += len(elasticsearch_entailments) - 1
            research_fields[instance['research_field']['id']]['tp'] += 1
            research_fields[instance['research_field']['id']]['fp'] += len(elasticsearch_entailments) - 1
        else:
            accuracy += n_templates - len(elasticsearch_entailments)
            fp += len(elasticsearch_entailments)
            research_fields[instance['research_field']['id']]['fp'] += len(elasticsearch_entailments)

    metrics = compute_metrics(len(instances), n_templates, accuracy, tp, fp, research_fields)
    test_set['metrics'] = metrics
    Writer.write_json(test_set, extend_path(test_set_path, '_es_evaluated'))

    plot = plot_research_fields_f_measures(metrics)
    Writer.write_png(plot, os.path.join(os.path.split(test_set_path)[0], 'es_results.png'))

    return metrics


def evaluate_scibert(test_set_path):
    test_set = Reader.read_json(test_set_path)

    # including the neutral template
    n_templates = len(list(set([entailment['template_id'] for entailment in test_set['entailments']]))) + 1

    accuracy = 0
    tp = 0
    fp = 0
    instances = test_set['entailments'] + test_set['contradictions'] + test_set['neutrals']
    research_fields = init_research_fields_metrics(instances)

    for i, instance in enumerate(instances):
        print('{}/{} - instance {}'.format(i + 1, len(instances), instance['instance_id']))
        instance['results'] = predict.predict_scibert(instance['hypothesis'])

        bert_entailments = instance['results'][:1]  # ignore fp
        bert_results = extract_top_k_results(bert_entailments, 1)

        if instance['target'] == 'entailment':
            # there is a hit in the response
            if instance['template_id'] in bert_results:
                accuracy += n_templates - len(bert_entailments) + 1
                tp += 1
                fp += len(bert_entailments) - 1
                research_fields[instance['research_field']['id']]['tp'] += 1
                research_fields[instance['research_field']['id']]['fp'] += len(bert_entailments) - 1
            # there is no hit in the response
            else:
                accuracy += n_templates - len(bert_entailments)
                fp += len(bert_entailments)
                research_fields[instance['research_field']['id']]['fp'] += len(bert_entailments)

        elif instance['target'] == 'neutral':
            # the number of entailments controls the accuracy of the neutrals.
            accuracy += n_templates - len(bert_entailments)
            fp += len(bert_entailments)
            research_fields[instance['research_field']['id']]['fp'] += len(bert_entailments)

            if not bert_results:
                tp += 1
                research_fields[instance['research_field']['id']]['tp'] += 1

    metrics = compute_metrics(len(instances), n_templates, accuracy, tp, fp, research_fields)
    test_set['metrics'] = metrics
    Writer.write_json(test_set, extend_path(test_set_path, '_scibert_evaluated'))

    plot = plot_research_fields_f_measures(metrics)
    Writer.write_png(plot, os.path.join(os.path.split(test_set_path)[0], 'scibert_results.png'))

    return metrics


def evaluate_baseline(test_set_path):
    test_set = Reader.read_json(test_set_path)

    # including the neutral template
    n_templates = len(list(set([entailment['template_id'] for entailment in test_set['entailments']]))) + 1

    accuracy = 0
    tp = 0
    fp = 0
    instances = test_set['entailments'] + test_set['contradictions'] + test_set['neutrals']
    research_fields = init_research_fields_metrics(instances)

    for i, instance in enumerate(instances):
        print('{}/{} - instance {}'.format(i + 1, len(instances), instance['instance_id']))
        instance['results'] = predict.predict_baseline(instance['research_field']['id'])  # here the trick

        baseline_entailments = instance['results'][:1]  # ignore fp
        baseline_results = extract_top_k_results(instance['results'], 1)

        # Baseline does not differentiate between entailments and neutrals.
        if instance['template_id'] in baseline_results:
            accuracy += n_templates - len(baseline_entailments) + 1
            tp += 1
            fp += len(baseline_entailments) - 1
            research_fields[instance['research_field']['id']]['tp'] += 1
            research_fields[instance['research_field']['id']]['fp'] += len(baseline_entailments) - 1
        else:
            accuracy += n_templates - len(baseline_entailments)
            fp += len(baseline_entailments)
            research_fields[instance['research_field']['id']]['fp'] += len(baseline_entailments)

    metrics = compute_metrics(len(instances), n_templates, accuracy, tp, fp, research_fields)
    test_set['metrics'] = metrics
    Writer.write_json(test_set, extend_path(test_set_path, '_baseline_evaluated'))

    plot = plot_research_fields_f_measures(metrics)
    Writer.write_png(plot, os.path.join(os.path.split(test_set_path)[0], 'baseline_results.png'))

    return metrics


def evaluate_baseline_full(test_set_path):
    test_set = Reader.read_json(test_set_path)

    # including the neutral template
    n_templates = len(list(set([entailment['template_id'] for entailment in test_set['entailments']]))) + 1

    accuracy = 0
    tp = 0
    fp = 0
    instances = test_set['entailments'] + test_set['contradictions'] + test_set['neutrals']
    research_fields = init_research_fields_metrics(instances)

    for i, instance in enumerate(instances):
        print('{}/{} - instance {}'.format(i + 1, len(instances), instance['instance_id']))
        instance['results'] = predict.predict_baseline_full(instance['research_field']['id'])  # here the trick

        baseline_entailments = instance['results'][:1]  # ignore fp
        baseline_results = extract_top_k_results(instance['results'], 1)

        # Baseline does not differentiate between entailments and neutrals.
        if instance['template_id'] in baseline_results:
            accuracy += n_templates - len(baseline_entailments) + 1
            tp += 1
            fp += len(baseline_entailments) - 1
            research_fields[instance['research_field']['id']]['tp'] += 1
            research_fields[instance['research_field']['id']]['fp'] += len(baseline_entailments) - 1
        else:
            accuracy += n_templates - len(baseline_entailments)
            fp += len(baseline_entailments)
            research_fields[instance['research_field']['id']]['fp'] += len(baseline_entailments)

    metrics = compute_metrics(len(instances), n_templates, accuracy, tp, fp, research_fields)
    test_set['metrics'] = metrics
    Writer.write_json(test_set, extend_path(test_set_path, '_baseline_full_evaluated'))

    plot = plot_research_fields_f_measures(metrics)
    Writer.write_png(plot, os.path.join(os.path.split(test_set_path)[0], 'baseline_full_results.png'))

    return metrics


def init_research_fields_metrics(instances):
    research_fields = {}

    for instance in instances:
        if instance['research_field']['id'] not in research_fields:
            research_fields[instance['research_field']['id']] = {
                'label': instance['research_field']['label'],
                'tp': 0,
                'fp': 0,
                'n_instances': 1
            }
        else:
            research_fields[instance['research_field']['id']]['n_instances'] += 1

    return research_fields


def extract_top_k_results(objects, k):
    top_k = []

    for object in objects[:k]:
        top_k.append(object['template_id'])

    return top_k


def compute_metrics(n_instances, n_templates, accuracy, tp, fp, research_fields):
    for id in research_fields.keys():
        recall = research_fields[id]['tp'] / research_fields[id]['n_instances']

        try:
            precision = research_fields[id]['tp'] / (research_fields[id]['tp'] + research_fields[id]['fp'])
        except ZeroDivisionError:
            precision = 0.0

        research_fields[id]['recall'] = recall
        research_fields[id]['precision'] = precision

        try:
            research_fields[id]['f1'] = (2 * precision * recall) / (precision + recall)
        except ZeroDivisionError:
            research_fields[id]['f1'] = 0.0

    recall = tp / n_instances
    precision = tp / (tp + fp)
    return {
        'accuracy': accuracy / (n_instances * n_templates),
        'recall': recall,
        'precision': precision,
        'f1': (2 * precision * recall) / (precision + recall),
        'research_fields': research_fields
    }


def main(config=None):
    args = config or parse_args()

    assert args.approach, 'approach must be provided.'
    assert args.test_set_path, 'test_set_path must be provided.'

    print('Evaluating {}...'.format(args.approach))
    results = {
        'elasticsearch': evaluate_elasticsearch,
        'scibert': evaluate_scibert,
        'baseline': evaluate_baseline,
        'baseline_full': evaluate_baseline_full
    }[args.approach](args.test_set_path)

    print(results)


if __name__ == '__main__':
    main()
