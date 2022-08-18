import os
import re

import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer, BertForSequenceClassification

from src import MODELS_DIR, PROCESSED_DATA_DIR
from src.util.io import Reader


class TemplateSimilarityPredictor:
    __instance = None
    BERT_TOKENIZER_PATH ='allenai/scibert_scivocab_uncased'
    BERT_NLI_PATH = os.path.join(MODELS_DIR, 'orkgnlp-templates-recommendation-scibert')
    DATASET_PATH = os.path.join(PROCESSED_DATA_DIR, 'dataset.json')
    MAX_SEQUENCE_LENGTH = 512
    CLASSES = {
        '0': 'entailment',
        '1': 'contradiction',
        '2': 'neutral'
    }

    def __init__(self):
        if TemplateSimilarityPredictor.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            TemplateSimilarityPredictor.__instance = self

        self.device = torch.device('cpu')
        self.bert_tokenizer = BertTokenizer.from_pretrained(TemplateSimilarityPredictor.BERT_TOKENIZER_PATH)
        self.bert_nli_model = BertForSequenceClassification.from_pretrained(TemplateSimilarityPredictor.BERT_NLI_PATH)

    @staticmethod
    def get_instance():
        if TemplateSimilarityPredictor.__instance:
            return TemplateSimilarityPredictor.__instance

        return TemplateSimilarityPredictor()

    def predict_similar_templates(self, q):
        similar_templates = []

        # We iterate the templates the model trained on to produce the class in the service perspective.
        data = Reader.read_json(TemplateSimilarityPredictor.DATASET_PATH)

        for template in data['templates']:
            premise = '{} {}'.format(
                template['label'],
                ' '.join([property for property in template['properties']])
            )

            label, score = self.predict_similar_template(premise, q)

            if TemplateSimilarityPredictor.CLASSES[str(label)] == 'entailment':
                similar_templates.append({
                    'template_id': template['id'],
                    'label': template['label'],
                    'score': score,
                })

        similar_templates = sorted(similar_templates, key=lambda i: i['score'], reverse=True)

        return similar_templates

    def predict_similar_template(self, template_string, paper_string):
        self.bert_nli_model.eval()

        # premise = templates_string, hypothesis = paper_string
        sequence = '[CLS] {} [SEP] {} [SEP]'.format(Utils.post_process(template_string),
                                                    Utils.post_process(paper_string))
        sequence_tokens = self.bert_tokenizer.tokenize(sequence)

        attention_mask = Utils.get_attention_mask(sequence_tokens)[:TemplateSimilarityPredictor.MAX_SEQUENCE_LENGTH]
        token_type = Utils.get_token_type(sequence_tokens)[:TemplateSimilarityPredictor.MAX_SEQUENCE_LENGTH]
        sequence_tokens = self.bert_tokenizer.convert_tokens_to_ids(sequence_tokens)[
                          :TemplateSimilarityPredictor.MAX_SEQUENCE_LENGTH]

        attention_mask = torch.tensor(attention_mask).unsqueeze(0).to(self.device)
        token_type = torch.tensor(token_type).unsqueeze(0).to(self.device)
        sequence_tokens = torch.tensor(sequence_tokens).unsqueeze(0).to(self.device)

        prediction = self.bert_nli_model(sequence_tokens, attention_mask, token_type)
        label = prediction.logits.argmax(dim=-1).item()
        score = prediction.logits[0][label].item()

        return label, score


class Utils:

    @staticmethod
    def get_attention_mask(tokens):
        return [1] * len(tokens)

    @staticmethod
    def get_token_type(tokens):
        sep_index = tokens.index('[SEP]') + 1
        return [0] * sep_index + [1] * (len(tokens) - sep_index)

    @staticmethod
    def post_process(string, is_query=False):
        if not string:
            return string

        # replace each occurrence of one of the following characters with ' '
        characters = ['\s+-\s+', '-', '_', '\.']
        regex = '|'.join(characters)
        string = re.sub(regex, ' ', string)

        # terms are lower-cased and only separated by a space character
        return ' '.join(string.split()).lower()
