import math
import os
import random
from collections import Counter

from src import PROCESSED_DATA_DIR
from src.util import string
from src.util.io import Reader, Writer

TRAINING_ENTAILMENTS_SIZE = 0.8
TRAINING_NEUTRALS_SIZE = 0.8
TRAINING_CONTRADICTIONS_THRESHOLD = 0.4
NEUTRAL_CONTRADICTIONS_THRESHOLD = 4
VALIDATION_SET_THRESHOLD = 0.1
random.seed(10)


def extract_premise(template):
    return extract_premise_hypothesis(template, {'label': None, 'abstract': None})[0]


def extract_hypothesis(paper):
    return extract_premise_hypothesis({'label': '', 'properties': []}, paper)[1]


def extract_premise_hypothesis(template, paper):
    premise = '{} {}'.format(
        template['label'],
        ' '.join([property for property in template['properties']])
    )

    hypothesis = '{} {}'.format(
        paper['label'],
        paper['abstract']
    )

    return premise, hypothesis


def get_template_by_id(templates, template_id):
    for template in templates:
        if template['id'] == template_id:
            return template

    return None


def training_set_entailments(dataset, training_set, training_instance_ids, n_papers):
    while len(training_set['entailments']) < TRAINING_ENTAILMENTS_SIZE * n_papers:
        random_template = random.choice(dataset['templates'])
        template_occurrences = dict(Counter([instance['template_id'] for instance in training_set['entailments']]))

        if random_template['id'] in template_occurrences and len(random_template['papers']) - template_occurrences[
            random_template['id']] <= 1:
            continue

        random_paper = random.choice(random_template['papers'])
        instance_id = '{}x{}'.format(random_template['id'], random_paper['id'])

        if instance_id in training_instance_ids:
            continue

        training_instance_ids.append(instance_id)
        premise, hypothesis = extract_premise_hypothesis(random_template, random_paper)
        instance = {
            'instance_id': instance_id,
            'template_id': random_template['id'],
            'paper_id': random_paper['id'],
            'premise': premise,
            'hypothesis': hypothesis,
            'sequence': '{} {}'.format(premise, hypothesis),
            'target': 'entailment',
            'research_field': random_paper['research_field']
        }

        training_set['entailments'].append(instance)


def test_set_entailments(dataset, test_set, test_instance_ids, training_instance_ids, training_paper_ids):
    test_paper_ids = []

    for template in dataset['templates']:
        for paper in template['papers']:
            instance_id = '{}x{}'.format(template['id'], paper['id'])

            if instance_id in training_instance_ids or paper['id'] in training_paper_ids or paper[
                'id'] in test_paper_ids:
                continue

            test_instance_ids.append(instance_id)
            test_paper_ids.append(paper['id'])
            premise, hypothesis = extract_premise_hypothesis(template, paper)
            instance = {
                'instance_id': instance_id,
                'template_id': template['id'],
                'paper_id': paper['id'],
                'premise': premise,
                'hypothesis': hypothesis,
                'sequence': '{} {}'.format(premise, hypothesis),
                'target': 'entailment',
                'research_field': paper['research_field']
            }

            test_set['entailments'].append(instance)


def training_set_neutrals(dataset, training_set, training_instance_ids, n_papers):
    for neutral_paper in dataset['neutral_papers']:
        if len(training_set['neutrals']) >= TRAINING_NEUTRALS_SIZE * n_papers:
            break

        instance_id = neutral_paper['id']

        if instance_id in training_instance_ids:
            continue

        training_instance_ids.append(instance_id)
        hypothesis = extract_hypothesis(neutral_paper)
        instance = {
            'instance_id': instance_id,
            'template_id': None,
            'paper_id': instance_id,
            'premise': None,
            'hypothesis': hypothesis,
            'sequence': hypothesis,
            'target': 'neutral',
            'research_field': neutral_paper['research_field']
        }

        training_set['neutrals'].append(instance)


def test_set_neutrals(dataset, test_set, test_instance_ids, training_instance_ids):
    for neutral_paper in dataset['neutral_papers']:
        instance_id = neutral_paper['id']

        if instance_id in test_instance_ids + training_instance_ids:
            continue

        test_instance_ids.append(instance_id)
        hypothesis = extract_hypothesis(neutral_paper)
        instance = {
            'instance_id': instance_id,
            'template_id': None,
            'paper_id': instance_id,
            'premise': None,
            'hypothesis': hypothesis,
            'sequence': hypothesis,
            'target': 'neutral',
            'research_field': neutral_paper['research_field']
        }

        test_set['neutrals'].append(instance)


def training_set_contradictions(dataset, training_set, training_instance_ids, test_paper_ids):
    template_occurrences = dict(Counter([instance['template_id'] for instance in training_set['entailments']]))

    for template_id, template_occurrence in template_occurrences.items():
        number_of_contradictions = math.ceil(template_occurrence * TRAINING_CONTRADICTIONS_THRESHOLD)

        while number_of_contradictions > 0:
            random_template = random.choice(dataset['templates'])

            # we are looking for papers from another templates
            if random_template['id'] == template_id:
                continue

            random_paper = random.choice(random_template['papers'])
            instance_id = '{}x{}'.format(template_id, random_paper['id'])

            # we are looking for a new instance and a paper that has not been selected for testing
            if instance_id in training_instance_ids or random_paper['id'] in test_paper_ids:
                continue

            training_instance_ids.append(instance_id)

            premise, hypothesis = extract_premise_hypothesis(get_template_by_id(dataset['templates'], template_id),
                                                             random_paper)
            instance = {
                'instance_id': instance_id,
                'template_id': template_id,
                'correct_template_id': random_template['id'],
                'paper_id': random_paper['id'],
                'premise': premise,
                'hypothesis': hypothesis,
                'sequence': '{} {}'.format(premise, hypothesis),
                'target': 'contradiction',
                'research_field': random_paper['research_field']
            }

            training_set['contradictions'].append(instance)
            number_of_contradictions -= 1


def training_set_neutral_contradictions(dataset, training_set, training_instance_ids, test_paper_ids):
    for object in training_set['neutrals']:

        for _ in range(NEUTRAL_CONTRADICTIONS_THRESHOLD):
            random_template = random.choice(dataset['templates'])

            instance_id = '{}x{}'.format(random_template['id'], object['paper_id'])

            # we are looking for a new instance and a paper that has not been selected for testing
            if instance_id in training_instance_ids or object['paper_id'] in test_paper_ids:
                continue

            training_instance_ids.append(instance_id)
            premise = extract_premise(random_template)
            hypothesis = object['hypothesis']

            instance = {
                'instance_id': instance_id,
                'template_id': random_template['id'],
                'correct_template_id': object['template_id'],
                'paper_id': object['paper_id'],
                'premise': premise,
                'hypothesis': hypothesis,
                'sequence': '{} {}'.format(premise, hypothesis),
                'target': 'contradiction',
                'research_field': object['research_field']
            }

            training_set['contradictions'].append(instance)


def test_set_contradictions(dataset, test_set, test_instance_ids, training_instance_ids, training_paper_ids, target):
    test_templates = [instance['template_id'] for instance in test_set['entailments']]

    for object in test_set[target]:
        for template in dataset['templates']:

            # we are looking for papers from another templates
            if target == 'neutrals':
                if template['id'] == object['template_id']:
                    continue

            # only consider those that used in the test set
            if template['id'] not in test_templates:
                continue

            instance_id = '{}x{}'.format(template['id'], object['paper_id'])

            # we are looking for a new instance and a paper that has been selected only for testing
            if instance_id in test_instance_ids + training_instance_ids or object['paper_id'] in training_paper_ids:
                continue

            test_instance_ids.append(instance_id)
            premise = extract_premise(template)
            hypothesis = object['hypothesis']

            instance = {
                'instance_id': instance_id,
                'template_id': template['id'],
                'correct_template_id': object['template_id'],
                'paper_id': object['paper_id'],
                'premise': premise,
                'hypothesis': hypothesis,
                'sequence': '{} {}'.format(premise, hypothesis),
                'target': 'contradiction',
                'research_field': object['research_field']
            }

            test_set['contradictions'].append(instance)


def split_dataset(dataset):
    n_papers = len([paper['id'] for template in dataset['templates'] for paper in template['papers']])
    training_set = {'entailments': [], 'contradictions': [], 'neutrals': []}
    test_set = {'entailments': [], 'contradictions': [], 'neutrals': []}
    training_instance_ids, test_instance_ids = [], []

    # prepare entailments
    training_set_entailments(dataset, training_set, training_instance_ids, n_papers)
    training_paper_ids = [entailment['paper_id'] for entailment in training_set['entailments']]
    test_set_entailments(dataset, test_set, test_instance_ids, training_instance_ids, training_paper_ids)

    # prepare neutrals
    training_set_neutrals(dataset, training_set, training_instance_ids, n_papers)
    test_set_neutrals(dataset, test_set, test_instance_ids, training_instance_ids)

    # prepare contradictions
    test_paper_ids = [entailment['paper_id'] for entailment in test_set['entailments']]
    training_set_contradictions(dataset, training_set, training_instance_ids, test_paper_ids)
    training_set_neutral_contradictions(dataset, training_set, training_instance_ids, test_paper_ids)

    test_set_contradictions(dataset, test_set, test_instance_ids, training_instance_ids, training_paper_ids,
                            'entailments')
    test_set_contradictions(dataset, test_set, test_instance_ids, training_instance_ids, training_paper_ids, 'neutrals')

    print('### Verifying ###')
    print('Training set instances are unique: ', len(training_instance_ids) == len(list(set(training_instance_ids))))
    print('Test set instances are unique: ', len(test_instance_ids) == len(list(set(test_instance_ids))))
    print('Training and test sets are disjoint', not bool(set(test_instance_ids).intersection(training_instance_ids)))

    training_paper_ids = [entailment['paper_id'] for entailment in training_set['entailments']]
    test_paper_ids = [entailment['paper_id'] for entailment in test_set['entailments']]

    print('Training and test papers are disjoint', not bool(set(training_paper_ids).intersection(test_paper_ids)))
    # This is ok, because one paper can use different templates
    print('Training papers are unique: ', len(training_paper_ids) == len(list(set(training_paper_ids))))
    # This must be true, because we don't want duplicates
    print('Test papers are unique: ', len(test_paper_ids) == len(list(set(test_paper_ids))))

    Writer.write_json(training_set, os.path.join(PROCESSED_DATA_DIR, 'training_set.json'))
    Writer.write_json(test_set, os.path.join(PROCESSED_DATA_DIR, 'test_set.json'))

    return training_set, test_set


def split_training_set(training_set):
    validation_set = {'entailments': [], 'contradictions': [], 'neutrals': []}

    for target in validation_set.keys():

        validation_set_size = math.ceil(len(training_set[target]) * VALIDATION_SET_THRESHOLD)

        for _ in range(validation_set_size):
            random_instance = random.choice(training_set[target])
            validation_set[target].append(random_instance)
            training_set[target].remove(random_instance)

    Writer.write_json(training_set, os.path.join(PROCESSED_DATA_DIR, 'training_set.json'))
    Writer.write_json(validation_set, os.path.join(PROCESSED_DATA_DIR, 'validation_set.json'))

    return training_set, validation_set


def reduce_test_set(test_set):
    test_set_reduced = {
        'entailments': test_set['entailments'],
        'contradictions': [],
        'neutrals': test_set['neutrals']
    }
    return test_set_reduced


def post_process(subset, subset_name):
    for target in subset.keys():
        for instance in subset[target]:
            instance['premise'] = string.post_process(instance['premise'])
            instance['hypothesis'] = string.post_process(instance['hypothesis'])
            instance['sequence'] = string.create_sequence(instance['premise'], instance['hypothesis'])

    Writer.write_json(subset, os.path.join(PROCESSED_DATA_DIR, '{}.json'.format(subset_name)))


def main(dataset):
    training_set, test_set = split_dataset(dataset)
    post_process(training_set, 'es_training_set')

    training_set, validation_set = split_training_set(training_set)
    test_set = reduce_test_set(test_set)

    print('----------------------')
    print('### Statistics ###')

    print('Dataset:')
    print('\tTemplates: {}'.format(len(dataset['templates'])))
    print('\tTemplated papers: {}'.format(len([paper['id']
                                               for template in dataset['templates']
                                               for paper in template['papers']])))
    print('\tNeutral papers: {}'.format(len(dataset['neutral_papers'])))
    print('\tTemplated research fields: {}'.format(len(list(set([paper['research_field']['id']
                                                                 for template in dataset['templates']
                                                                 for paper in template['papers']])))))
    print('\tNeutral research fields: {}'.format(len(list(set([paper['research_field']['id']
                                                               for paper in dataset['neutral_papers']])))))

    print('Training instances:')
    print('\tEntailments: {}'.format(len(training_set['entailments'])))
    print('\tContradictions: {}'.format(len(training_set['contradictions'])))
    print('\tNeutrals: {}'.format(len(training_set['neutrals'])))
    print('\tSum: {}'.format(
        len(training_set['entailments']) + len(training_set['contradictions']) + len(training_set['neutrals'])))

    print('Test instances:')
    print('\tEntailments: {}'.format(len(test_set['entailments'])))
    print('\tContradictions: {}'.format(len(test_set['contradictions'])))
    print('\tNeutrals: {}'.format(len(test_set['neutrals'])))
    print(
        '\tSum: {}'.format(len(test_set['entailments']) + len(test_set['contradictions']) + len(test_set['neutrals'])))

    print('Validation instances:')
    print('\tEntailments: {}'.format(len(validation_set['entailments'])))
    print('\tContradictions: {}'.format(len(validation_set['contradictions'])))
    print('\tNeutrals: {}'.format(len(validation_set['neutrals'])))
    print('\tSum: {}'.format(
        len(validation_set['entailments']) + len(validation_set['contradictions']) + len(validation_set['neutrals'])))

    post_process(training_set, 'training_set')
    post_process(test_set, 'test_set')
    post_process(validation_set, 'validation_set')


if __name__ == '__main__':
    dataset = Reader.read_json(os.path.join(PROCESSED_DATA_DIR, 'dataset.json'))
    main(dataset)
