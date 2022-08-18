import io
import matplotlib.pyplot as plt

from PIL import Image

from src.util.string import uri_to_id

plt.rcParams["figure.figsize"] = (20, 10)


def plot_templates_research_fields_intersection_papers(research_fields):
    plt.clf()
    fig, ax = plt.subplots()
    width = 0.3

    x_labels = [uri_to_id(research_field) for research_field in research_fields.keys()]
    template_contributions = {uri_to_id(template['template_id']) : [] for field in list(research_fields.values()) for template in field['templates']}

    for research_field in research_fields:
        for template in research_fields[research_field]['templates']:
            length = len(template['papers'])
            template_contributions[uri_to_id(template['template_id'])].append(length)

    bottom = [0] * len(research_fields.keys())
    for template_contribution in template_contributions:
        bar_plot = ax.bar(x_labels, template_contributions[template_contribution], width, bottom=bottom, label='{}'.format(template_contribution))
        bottom = [sum(x) for x in zip(bottom, template_contributions[template_contribution])]

    heights = []
    for research_field in research_fields:

        contributions = 0
        for template in research_fields[research_field]['templates']:
            contributions += len(template['papers'])

        heights.append(contributions)

    for idx, rect in enumerate(bar_plot):
        ax.text(rect.get_x() + rect.get_width() / 2. - rect.get_width(), 0.5 * heights[idx],
                list(research_fields.values())[idx]['label'],
                ha='center', va='bottom', rotation=90)

    plt.legend(loc='best', ncol=8)
    plt.xlabel('Research fields of templates')
    plt.ylabel('# Papers using template T and have the same research field of T')
    #plt.title('Distribution of contributions and used templates having the same research field')
    axes = plt.gca()
    axes.set_ylim([0, 80])

    return convert_plot_to_object(plt)


def plot_templates_research_fields_intersection_other_papers(research_fields):
    plt.clf()
    fig, ax = plt.subplots()
    width = 0.3

    x_labels = [uri_to_id(research_field) for research_field in research_fields.keys()]
    template_contributions = {uri_to_id(template['template_id']): [] for field in list(research_fields.values()) for
                              template in field['templates']}

    for research_field in research_fields:
        for template in research_fields[research_field]['templates']:
            length = len(template['other_papers'])
            template_contributions[uri_to_id(template['template_id'])].append(length)

    bottom = [0] * len(research_fields.keys())
    for template_contribution in template_contributions:
        bar_plot = ax.bar(x_labels, template_contributions[template_contribution], width, bottom=bottom,
                          label='{}'.format(template_contribution))
        bottom = [sum(x) for x in zip(bottom, template_contributions[template_contribution])]

    heights = []
    for research_field in research_fields:

        contributions = 0
        for template in research_fields[research_field]['templates']:
            contributions += len(template['other_papers'])

        heights.append(contributions)

    for idx, rect in enumerate(bar_plot):
        ax.text(rect.get_x() + rect.get_width() / 2. - rect.get_width(), 0.5 * heights[idx],
                list(research_fields.values())[idx]['label'],
                ha='center', va='bottom', rotation=90)

    plt.legend(loc='best', ncol=8)
    plt.xlabel('Research fields of templates')
    plt.ylabel('# Papers using template T and have the same research field of T')
    # plt.title('Distribution of contributions and used templates having the same research field')
    axes = plt.gca()
    axes.set_ylim([0, 80])

    return convert_plot_to_object(plt)


def plot_templates_research_fields_papers(research_fields):
    plt.clf()
    fig, ax = plt.subplots()

    n_templates = []
    for research_field in research_fields.values():
        n_templates.append(len([template for template in research_field['templates']
                                if template['papers'] or template['other_papers']]))

    bar_plot = plt.bar([uri_to_id(key) for key in research_fields.keys()],
                       n_templates,
                       width=0.4)

    for idx, rect in enumerate(bar_plot):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2. - rect.get_width(), 0.25 * height,
                list(research_fields.values())[idx]['label'],
                ha='center', va='bottom', rotation=90)

    plt.xlabel('Research fields')
    plt.ylabel('# Templates')
    plt.title('Distribution of templates over research fields')

    return convert_plot_to_object(plt)


def plot_papers_research_fields(research_fields):
    plt.clf()
    fig, ax = plt.subplots()

    bar_plot = plt.bar([uri_to_id(key) for key in research_fields.keys()],
                       [len(research_field['papers']) for research_field in research_fields.values()],
                       width=0.4)

    for idx, rect in enumerate(bar_plot):
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2. - rect.get_width(), 0.25 * height,
                list(research_fields.values())[idx]['label'],
                ha='center', va='bottom', rotation=90)

    plt.xlabel('Research fields')
    plt.ylabel('# Papers')
    plt.title('Distribution of papers over research fields')

    return convert_plot_to_object(plt)


def plot_papers_research_fields_and_their_templates(research_fields):
    plt.clf()
    fig, ax = plt.subplots()
    width = 0.3

    x_labels = [uri_to_id(research_field) for research_field in research_fields.keys()]
    template_papers = {uri_to_id(template['id']): [] for template in list(research_fields.values())[0]['templates']}

    for research_field in research_fields:
        for template in research_fields[research_field]['templates']:
            length = len(template['papers'])
            template_papers[uri_to_id(template['id'])].append(length)

    bottom = [0] * len(research_fields.keys())
    for template_paper in template_papers:
        bar_plot = ax.bar(x_labels, template_papers[template_paper], width, bottom=bottom, label='{}'.format(template_paper))
        bottom = [sum(x) for x in zip(bottom, template_papers[template_paper])]

    heights = []
    for research_field in research_fields:

        contributions = 0
        for template in research_fields[research_field]['templates']:
            contributions += len(template['papers'])

        heights.append(contributions)

    for idx, rect in enumerate(bar_plot):
        ax.text(rect.get_x() + rect.get_width() / 2. - rect.get_width(), 0.5 * heights[idx],
                list(research_fields.values())[idx]['label'],
                ha='center', va='bottom', rotation=90)

    plt.legend(loc='best', ncol=8)
    plt.xlabel('Research fields of papers')
    plt.ylabel('# Papers using template T')
    #plt.title('Distribution of contributions over their research fields w.r.t. the used templates')
    axes = plt.gca()
    axes.set_ylim([0, 80])

    return convert_plot_to_object(plt)


def plot_research_fields_f_measures(metrics):
    plt.clf()
    fig, ax = plt.subplots()

    bar_plot = plt.bar([key for key in metrics['research_fields'].keys()],
                       [research_field['f1'] for research_field in metrics['research_fields'].values()],
                       width=0.4)

    for idx, rect in enumerate(bar_plot):
        ax.text(rect.get_x() + rect.get_width() / 2. - rect.get_width(),
                0.25 * rect.get_height(),
                list(metrics['research_fields'].values())[idx]['label'],
                ha='center', va='bottom', rotation=90)

        ax.text(rect.get_x() + rect.get_width() / 2.,
                rect.get_height() + 0.01,
                list(metrics['research_fields'].values())[idx]['n_instances'],
                ha='center', rotation=0)

    plt.xlabel('Research fields')
    plt.ylabel('F1-Score')
    plt.title('F1-Scores over {} research fields. Numbers on bars represent '
              'the number of test instances for the respective field.'.format(len(metrics['research_fields'].keys())))

    fig.text(0.4, 0.95,
             'Micro F1-Score: {:.3f}'.format(metrics['f1'] * 1000 / 1000),
             fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    return convert_plot_to_object(plt)


def convert_plot_to_object(plt):
    """ converts matplotlib object into a PIL image object """
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    im = Image.open(buf)

    return im
