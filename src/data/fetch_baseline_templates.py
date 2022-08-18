import os

from src import TRIPLE_STORE_URL, RAW_DATA_DIR
from src.data.sparql.queries import TEMPLATES_RESEARCH_FIELDS
from src.data.sparql.service import query
from src.util.io import Writer


def to_json(df):
    uri_columns = ['template', 'templateOfResearchField']
    df[uri_columns] = df[uri_columns].applymap(lambda x: os.path.basename(str(x)))

    templates = []
    for template_id in df.template.unique():
        template_df = df[df.template == template_id]

        template_json = {
            'id': template_df.template.iloc[0],
            'label': template_df.templateLabel.iloc[0],
            'research_fields': [
                {'id': id, 'label': label}
                for (i, (id, label)) in template_df.loc[:, ['templateOfResearchField', 'templateOfResearchFieldLabel']
                                                        ].dropna().drop_duplicates().iterrows()
            ],
        }
        templates.append(template_json)

    return templates


def main():
    df = query(TRIPLE_STORE_URL, TEMPLATES_RESEARCH_FIELDS)
    templates = to_json(df)
    Writer.write_json({'templates': templates}, os.path.join(RAW_DATA_DIR, 'baseline_templates.json'))


if __name__ == '__main__':
    main()
