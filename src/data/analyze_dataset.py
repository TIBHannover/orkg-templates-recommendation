import os

from src import PROCESSED_DATA_DIR
from src.util.io import Reader, Writer
from src.util.string import uri_to_id
from src.util.visualization import plot_templates_research_fields_intersection_papers, \
    plot_templates_research_fields_intersection_other_papers, plot_templates_research_fields_papers, \
    plot_papers_research_fields, plot_papers_research_fields_and_their_templates


def extract_templates_research_fields(dataset):
    research_fields = {}

    for template in dataset['templates']:
        for research_field in template['research_fields']:
            if research_field['id']:
                if research_field['id'] not in research_fields:
                    research_fields[research_field['id']] = {'label': research_field['label'], 'templates': []}

    for research_field in research_fields:
        for template in dataset['templates']:
            if research_field in [field['id'] for field in template['research_fields']]:
                research_fields[research_field]['templates'].append({
                    'template_id': template['id'],
                    'papers': [paper['id'] for paper in template['papers']
                               if paper['research_field']['id'] == uri_to_id(research_field)],
                    'other_papers': [paper['id'] for paper in
                                     template['papers']
                                     if paper['research_field']['id'] != uri_to_id(research_field)]
            })
            else:
                research_fields[research_field]['templates'].append({
                    'template_id': template['id'],
                    'papers': [],
                    'other_papers': []
                })

    dataset['templates_research_fields'] = research_fields
    return dataset


def extract_papers_research_fields(dataset):
    research_fields = {}

    for template in dataset['templates']:
        for paper in template['papers']:

            if paper['research_field']['id'] not in research_fields:
                research_fields[paper['research_field']['id']] = {'label': '', 'papers': []}

            research_fields[paper['research_field']['id']]['label'] = paper['research_field']['label']
            research_fields[paper['research_field']['id']]['papers'].append(
                paper['id'])

    dataset['papers_research_fields'] = research_fields
    return dataset


def extract_papers_research_fields_and_their_templates(data):
    research_fields = {}

    for research_field in data['papers_research_fields']:
        research_fields[research_field] = {'label': data['papers_research_fields'][research_field]['label'], 'templates': []}

        for template in data['templates']:
            temp_template = {
                'id': template['id'],
                'papers': []
            }

            for paper in template['papers']:
                if paper['research_field']['id'] == research_field:
                    temp_template['papers'].append(paper['id'])

            research_fields[research_field]['templates'].append(temp_template)

    data['papers_research_fields_and_their_templates'] = research_fields
    return data


def extract_neutral_papers_research_fields(dataset):
    research_fields = {}

    for paper in dataset['neutral_papers']:

        if paper['research_field']['id'] not in research_fields:
            research_fields[paper['research_field']['id']] = {'label': '', 'papers': []}

        research_fields[paper['research_field']['id']]['label'] = paper['research_field']['label']
        research_fields[paper['research_field']['id']]['papers'].append(
            paper['id'])

    dataset['neutral_papers_research_fields'] = research_fields
    return dataset


def extract_all_papers_research_fields(dataset):
    all_research_fields = {}
    papers_research_fields = dataset['papers_research_fields']
    neutral_papers_research_fields = dataset['neutral_papers_research_fields']

    for neutral_research_field_id in list(neutral_papers_research_fields.keys()):
        if neutral_research_field_id in papers_research_fields:
            all_papers = papers_research_fields[neutral_research_field_id]['papers'] +\
                         neutral_papers_research_fields[neutral_research_field_id]['papers']
            all_research_fields[neutral_research_field_id] = {
                'label': neutral_papers_research_fields[neutral_research_field_id]['label'],
                'papers': all_papers
            }
        else:
            all_research_fields[neutral_research_field_id] = {
                'label': neutral_papers_research_fields[neutral_research_field_id]['label'],
                'papers': neutral_papers_research_fields[neutral_research_field_id]['papers']
            }

    dataset['all_papers_research_fields'] = all_research_fields
    return dataset


def main(dataset):
    dataset = extract_templates_research_fields(dataset)
    templates_research_fields_intersection_plot = plot_templates_research_fields_intersection_papers(
        dataset['templates_research_fields'])
    Writer.write_png(templates_research_fields_intersection_plot,
                     os.path.join(PROCESSED_DATA_DIR, 'templates_research_fields_intersection.png'))

    templates_research_fields_intersection_other_plot = plot_templates_research_fields_intersection_other_papers(
        dataset['templates_research_fields'])
    Writer.write_png(templates_research_fields_intersection_other_plot,
                     os.path.join(PROCESSED_DATA_DIR, 'templates_research_fields_intersection_other.png'))

    templates_research_fields_plot = plot_templates_research_fields_papers(dataset['templates_research_fields'])
    Writer.write_png(templates_research_fields_plot, os.path.join(PROCESSED_DATA_DIR, 'templates_research_fields.png'))

    dataset = extract_papers_research_fields(dataset)
    papers_research_fields_plot = plot_papers_research_fields(dataset['papers_research_fields'])
    Writer.write_png(papers_research_fields_plot, os.path.join(PROCESSED_DATA_DIR, 'papers_research_fields.png'))

    dataset = extract_papers_research_fields_and_their_templates(dataset)
    papers_research_fields_and_their_templates_plot = plot_papers_research_fields_and_their_templates(
        dataset['papers_research_fields_and_their_templates'])
    Writer.write_png(papers_research_fields_and_their_templates_plot,
                     os.path.join(PROCESSED_DATA_DIR, 'papers_research_fields_and_their_templates.png'))

    dataset = extract_neutral_papers_research_fields(dataset)
    neutral_papers_research_fields_plot = plot_papers_research_fields(dataset['neutral_papers_research_fields'])
    Writer.write_png(neutral_papers_research_fields_plot,
                     os.path.join(PROCESSED_DATA_DIR, 'neutral_papers_research_fields.png'))

    dataset = extract_all_papers_research_fields(dataset)
    all_papers_research_fields_plot = plot_papers_research_fields(dataset['all_papers_research_fields'])
    Writer.write_png(all_papers_research_fields_plot, os.path.join(PROCESSED_DATA_DIR, 'all_papers_research_fields.png'))

    Writer.write_json(dataset, os.path.join(PROCESSED_DATA_DIR, 'dataset_analyzed.json'))


if __name__ == '__main__':
    dataset = Reader.read_json(os.path.join(PROCESSED_DATA_DIR, 'dataset.json'))
    main(dataset)
